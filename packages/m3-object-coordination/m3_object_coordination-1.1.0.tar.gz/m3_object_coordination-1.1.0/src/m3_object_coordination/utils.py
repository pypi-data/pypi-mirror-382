# coding: utf-8
from datetime import date
from datetime import timedelta
from itertools import groupby
from operator import attrgetter
from typing import Generator
from typing import NoReturn
from typing import Optional
from typing import Tuple
from typing import TypeVar

from django.contrib.contenttypes.models import ContentType
from django.db.models import F
from django.db.models import Q
from django.db.models import QuerySet
from django.db.models.aggregates import Count
from django.db.models.base import Model
from django.db.transaction import atomic
from m3.actions import ActionPack
from m3.actions.exceptions import ApplicationLogicException

import m3_object_coordination

from ._external_utils.utils.db import get_original_field_values
from .constants import NEGATIVE_ROUTE_STATES
from .constants import RESETABLE_ROUTE_STATES
from .constants import ROUTE_STATE_NAMES
from .constants import MoveDirection
from .constants import PhaseState
from .constants import ReviewResult
from .constants import RouteState
from .models import Log
from .models import Route
from .models import RouteApproover
from .models import RoutePhase
from .models import RouteTemplate
from .models import RouteTemplatePhase
from .signals import route_phase_change_state
from .signals import route_phase_start


PhaseType = TypeVar('PhaseType', RouteTemplatePhase, RoutePhase)


def get_route_for(obj) -> Optional[Route]:
    """Возвращает маршрут согласования для указанного объекта."""
    if not m3_object_coordination.config.can_coordinate(obj):
        raise ValueError(
            f'Для объектов типа "{obj._meta.verbose_name}" не поддерживаются '
            'маршруты согласования.'
        )
    return Route.objects.filter(
        object_type=ContentType.objects.get_for_model(obj),
        object_id=obj.pk,
    ).first()


def get_route_state(route: Route) -> RouteState:
    """Возвращает состояние маршрута согласования.

    Возможные состояния описаны в
    :class:`m3_object_coordination.constants.RouteState`.
    """
    if not route.pk:
        raise ValueError('Маршрут должен быть создан в БД.')

    phases = RoutePhase.objects.filter(route=route)

    if not phases:
        result = RouteState.PREPARATION

    else:
        approovers_query = RouteApproover.objects.filter(
            phase__route=route
        ).order_by('phase')
        approovers = {phase.id: None for phase in phases}
        for phase_id, phase_approovers in groupby(
            approovers_query, attrgetter('phase_id')
        ):
            approovers[phase_id] = tuple(phase_approovers)

        if not approovers or any(not a for a in approovers.values()):
            result = RouteState.PREPARATION

        elif all(
            phase.actual_date is not None
            for phase in phases
        ):
            if Log.objects.filter(
                approover__phase__route=route,
                actual=True,
                result=ReviewResult.REJECTED,
            ).exists():
                result = RouteState.REJECTED

            elif Log.objects.filter(
                approover__phase__route=route,
                actual=True,
                result=ReviewResult.NEED_CHANGES,
            ).exists():
                result = RouteState.NEED_CHANGES

            else:
                result = RouteState.APPROOVED

        elif any(
            phase.planned_date is not None
            for phase in phases
        ):
            result = RouteState.EXECUTING

        else:
            result = RouteState.WAITING

    return result


def get_current_phase(route: Route) -> Optional[PhaseType]:
    """Возвращает текущий этап согласования объекта, если он существует.

    Текущим считается этап, следующий за последним согласованным этапом.
    Если маршрут согласования не было запущен, возвращает ``None``.
    Если маршрут в состоянии Согласован, то возвращает последний этап
    процесса согласования.

    :param route: маршрут согласования объекта.
    :return: текущий этап маршрута.
    """
    return RoutePhase.objects.order_by(
        'number',
    ).filter(
        route=route,
        planned_date__isnull=False,
        actual_date__isnull=True,
    ).first()


def get_previous_phase(phase: PhaseType) -> Optional[PhaseType]:
    """Возвращает предыдущий этап, если он существует.

    :param phase: этап маршрута согласования.
    :return: предыдущий этап маршрута.
    """
    return RoutePhase.objects.order_by(
        'number',
    ).filter(
        route_id=phase.route_id,
        number__lt=phase.number,
    ).first()


def get_next_phase(phase: PhaseType) -> Optional[PhaseType]:
    """Возвращает следующий этап, если он существует.

    :param phase: этап маршрута согласования.
    :return: следущий этап маршрута.
    """
    return RoutePhase.objects.order_by(
        'number',
    ).filter(
        route_id=phase.route_id,
        number__gt=phase.number,
    ).first()


def get_phase_approovers(phase: PhaseType) -> QuerySet:
    """Возвращает всех согласующих на этапе.

    :param phase: этап маршрута согласования.
    :return: кварисет согласующих объектов.
    """
    return RouteApproover.objects.filter(phase=phase)


@atomic
def swap_phases(phase1: PhaseType, phase2: PhaseType) -> NoReturn:
    """Меняет два этапа местами в порядке согласования."""
    # pylint: disable=no-else-raise
    if phase1.pk is None or phase2.pk is None:
        raise ValueError('Этапы должны быть созданы в БД.')

    if (
        isinstance(phase1, RouteTemplatePhase) and
        isinstance(phase2, RouteTemplatePhase) and
        phase1.template_id != phase2.template_id
    ):
        raise ValueError('Этапы должны принадлежать одному шаблону.')

    elif (
        isinstance(phase1, RoutePhase) and
        isinstance(phase2, RoutePhase) and
        phase1.route_id != phase2.route_id
    ):
        raise ValueError('Этапы должны принадлежать одному маршруту.')

    elif type(phase1) is not type(phase2):
        raise TypeError('Этапы должны быть одного типа.')

    phase1.refresh_from_db(fields=('number',))
    phase2.refresh_from_db(fields=('number',))
    number1, number2 = phase1.number, phase2.number

    phase1.number = 0
    phase1.full_clean()
    phase1.save(update_fields=('number',))

    phase2.number = number1
    phase2.full_clean()
    phase2.save(update_fields=('number',))

    phase1.number = number2
    phase1.full_clean()
    phase1.save(update_fields=('number',))


@atomic
def move_phases(direction: MoveDirection, *phases: PhaseType) -> NoReturn:
    """Перемещает этап на одну позицию вверх в указанном направлении.

    :param direction: Направление перемещения (False --- вверх, True --- вниз).
    :param phases: Этапы согласования.
    """
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    models = {type(obj) for obj in phases}
    if len(models) != 1:
        raise TypeError(
            'Допускается одновременное перемещение только этапов одного и '
            'того же типа.'
        )
    model = models.pop()
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    identities = {
        tuple(phase.get_phase_group_identity().items())
        for phase in phases
    }
    if len(identities) != 1:
        raise ValueError('Этапы принадлежат разным объектам.')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    identity = phases[0].get_phase_group_identity()
    all_phases = model.objects.filter(**identity)
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    if len({phase.id for phase in phases}) != len(phases):
        raise ValueError('Этапы дублируются.')
    if len({phase.number for phase in phases}) != len(phases):
        raise ValueError('Номера этапов дублируются.')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    threshold_number = (max if direction else min)(
        map(attrgetter('number'), all_phases)
    )
    if any(phase.number == threshold_number for phase in phases):
        raise ValueError('Невозможно переместить этапы.')
    # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    reordered_phases = []
    for phase in sorted(
        all_phases, key=lambda phase: phase.number, reverse=direction,
    ):
        reordered_phases.insert(1 if phase in phases else 0, phase)
    if not direction:
        reordered_phases = reversed(reordered_phases)

    all_phases.update(  # нужно для обхода ограничения уникальности
        number=F('number') + max(phase.number for phase in all_phases),
    )
    for new_number, phase in enumerate(reordered_phases, 1):
        phase.number = new_number
        phase.full_clean()
        phase.save(update_fields=('number',))


def move_phases_up(*phases: PhaseType) -> NoReturn:
    """Перемещает этап согласования на одну позицию вверх по порядку."""
    move_phases(MoveDirection.UP, *phases)


def move_phases_down(*phases: PhaseType) -> NoReturn:
    """Перемещает этап согласования на одну позицию вниз по порядку."""
    move_phases(MoveDirection.DOWN, *phases)


@atomic
def create_route_for(
    obj,
    template: RouteTemplate = None,
    date_of_creation: date = None,
) -> Route:
    """Создает маршрут согласования для указанного объекта.

    Если шаблон маршрута согласования не указан, то будет использован шаблон
    по умолчанию.

    Если для объекта уже был создан маршрут согласования и в журнале
    согласования объекта уже есть согласования. Иначе имеющийся маршрут
    удаляется и создается новый.

    :raises m3.actions.exceptions.ApplicationLogicException:

        - если в журнале согласования для указанного объекта есть записи;
        - если для объектов данного типа не определен шаблон маршрута
          согласования по умолчанию.
    """
    current_route = get_route_for(obj)
    if current_route:
        # pylint: disable=no-else-raise
        if Log.objects.filter(
            approover__phase__route=current_route,
        ).exists():
            raise ApplicationLogicException(
                'Пересоздание маршрута согласования невозможно, т.к. в '
                'журнале согласования объекта уже есть записи.'
            )
        else:
            current_route.delete()

    date_of_creation = date_of_creation or date.today()
    content_type = ContentType.objects.get_for_model(obj)

    if not template:
        template = RouteTemplate.objects.filter(
            RouteTemplate.get_date_in_intervals_filter(date_of_creation),
            object_type=content_type,
            default=True,
        ).first()
        if not template:
            raise ApplicationLogicException(
                'Создание маршрута согласования невозможно, т.к. для '
                f'объектов "{obj._meta.verbose_name}" не определен шаблон '
                'маршрута согласования по умолчанию.'
            )

    # У шаблона должны быть определены этапы.
    if not template.phases.exists():
        raise ApplicationLogicException(
            'Создание маршрута согласования невозможно, т.к. для  шаблона '
            f'"{template.name}" не определены этапы.'
        )

    # У шаблона должны быть определены согласующие на этапах.
    empty_phases = RouteTemplatePhase.objects.filter(
        template=template,
    ).annotate(
        dep_count=Count('approovers__id')
    ).filter(dep_count__lt=1)
    if empty_phases.exists():
        raise ApplicationLogicException(
            'Создание маршрута согласования невозможно, т.к. для  шаблона '
            f'"{template.name}" не определены согласующие на этапе.'
        )

    route = Route.objects.create(
        id=getattr(current_route, 'id', None),
        template=template,
        object=obj,
    )
    for template_phase in RouteTemplatePhase.objects.filter(
        template=template
    ).prefetch_related('approovers'):
        phase = RoutePhase.objects.create(
            route=route,
            number=template_phase.number,
            name=template_phase.name,
            deadline=template_phase.deadline,
            template=template_phase,
        )
        approovers = template_phase.approovers.all()
        for template_approover in approovers:
            RouteApproover.objects.create(
                phase=phase,
                approover_type_id=template_approover.approover_type_id,
                approover_id=template_approover.approover_id,
                template=template_approover,
            )

    return route


@atomic
def insert_phase(phase: PhaseType) -> NoReturn:
    """Добавляет этап согласования в указанную позицию в маршруте.

    Позиция этапа в маршруте согласования определяется значением атрибута
    ``number``. Если на указанной позиции уже есть этап, то этот и последующие
    этапы сдвигаются вперёд. В случае, если позиция этапа не является следующей
    за последним этапом, номер этапа уменьшается. Если позиция не указана, то
    этап добавляется в конец маршрута согласования.
    """
    if phase.pk:
        raise ValueError(
            'Функция не поддерживает работу с уже созданными этапами '
            'согласования.'
        )

    identity = phase.get_phase_group_identity()

    if any(value is None for value in identity.values()):
        raise ValueError('Не указан маршрут согласования.')

    phases_query = phase.__class__.objects.filter(**identity)

    if (
        phase.number and
        phases_query.filter(number=phase.number).exists()
    ):
        phases_query.filter(
            number__gte=phase.number
        ).update(
            number=F('number') + 1,
        )

    phase.clean_and_save()


def add_working_days(from_day: date, days_count: int) -> date:
    """Возвращает дату, отстоящую на указанное количество *рабочих* дней.

    Тип дня определяется с помощью
    :meth:`m3_object_coordination.Config.is_working_day`.

    :param from_day: исходная дата (отсчет начинается не с этой даты, а с
        первого рабочего дня, следующего за этой датой).
    :param days_count: количество рабочих дней, добавляемое к указанной дате.
    """
    delta = timedelta(days=-1 if days_count < 0 else 1)
    days_count = abs(days_count)

    day, counter = from_day, 0
    is_working_day = m3_object_coordination.config.is_working_day

    while not is_working_day(day):
        day += delta

    while counter < days_count:
        day += delta
        if is_working_day(day):
            counter += 1

    return day


def get_phase_state(phase: RoutePhase) -> Optional[PhaseState]:
    """Возвращает текущее состояние этапа согласования."""
    # pylint: disable=too-many-branches
    if phase.pk:
        if get_original_field_values(phase, 'actual_date'):
            phase_results = set(
                Log.objects.filter(
                    approover__phase=phase,
                    actual=True,
                ).values_list('result', flat=True)
            )

            if not phase_results:
                result = PhaseState.BLOCKED

            elif any(
                phase_result != ReviewResult.AGREED
                for phase_result in phase_results
            ):
                result = PhaseState.STOPPED

            elif all(
                phase_result == ReviewResult.AGREED
                for phase_result in phase_results
            ):
                result = PhaseState.EXECUTED

            else:
                result = None  # pragma: no cover

        else:
            previous_phase = phase.route.phases.filter(
                number__lt=phase.number,
            ).order_by('number').last()
            if previous_phase:
                if previous_phase.actual_date:
                    result = PhaseState.EXECUTING
                else:
                    result = PhaseState.WAITING
            else:  # Этап является первым.
                if get_original_field_values(phase, 'planned_date'):
                    result = PhaseState.EXECUTING
                else:
                    result = PhaseState.WAITING

    else:
        result = None  # pragma: no cover

    return result


@atomic
def set_review_result(
    approover: RouteApproover,
    result: ReviewResult,
    comment: Optional[str] = None,
    user: Optional[Model] = None,
    default_deadline: int = 1
) -> Log:
    """Проставляет отметку о рассмотрении и возвращает запись журнала.

    :param approover: согласующий на этапе маршрута.
    :param result: результат рассмотрения.
    :param comment: комментарий (обязателен при отказе в согласовании).
    :param user: пользователь, выполняющий согласование (пустое значение
        указывает на то, что согласование проведено автоматически Системой).
    :param default_deadline: нормативный срок согласования по умолчанию (дней),
        используется при определении плановой даты исполнения следующего этапа.
    """
    if get_phase_state(approover.phase) != PhaseState.EXECUTING:
        raise ApplicationLogicException(
            f'Этап "{approover.phase.name}" не находится на согласовании.'
        )

    # Создание записи в журнале согласования.
    log_record = Log.objects.create(
        approover=approover,
        result=result,
        comment=comment,
        user=user,
    )

    # Обновление параметров соответствующих этапов согласования.
    current_phase = approover.phase

    if result == ReviewResult.AGREED:
        if Log.objects.filter(
            approover__phase=current_phase,
            result=ReviewResult.AGREED,
            actual=True,
        ).count() == current_phase.approovers.count():
            # Этап полностью согласован, проставление даты согласования.
            current_phase.actual_date = log_record.timestamp.date()
            current_phase.full_clean()
            current_phase.save(update_fields=('actual_date',))
            route_phase_change_state.send(
                sender=None,
                phase=current_phase,
                src_state=PhaseState.EXECUTING,
                dst_state=PhaseState.EXECUTED,
            )

            next_phase = RoutePhase.objects.filter(
                route_id=current_phase.route_id,
                number__gt=current_phase.number,
            ).order_by('number').first()
            if next_phase:
                next_phase.planned_date = add_working_days(
                    date.today(), next_phase.deadline or default_deadline
                )
                next_phase.full_clean()
                next_phase.save(update_fields=('planned_date',))
                route_phase_start.send(None, phase=next_phase)
                route_phase_change_state.send(
                    sender=None,
                    src_state=PhaseState.WAITING,
                    dst_state=PhaseState.EXECUTING,
                )

    else:
        route_phase_change_state.send(
            sender=None,
            phase=current_phase,
            src_state=PhaseState.EXECUTING,
            dst_state=PhaseState.STOPPED,
        )

        # Этап не прошел согласование, все последющие также завершаются.
        for phase in RoutePhase.objects.filter(
            route_id=current_phase.route_id,
            number__gte=current_phase.number,
        ).order_by('number'):
            phase.actual_date = date.today()
            phase.full_clean()
            phase.save(update_fields=('actual_date',))
            route_phase_change_state.send(
                sender=None,
                src_state=PhaseState.WAITING,
                dst_state=PhaseState.BLOCKED,
            )

    return log_record


@atomic
def start_route(route: Route, default_deadline: int = 1) -> NoReturn:
    """Запускает маршрут согласования.

    При запуске маршрута проставляется плановая дата его завершения.

    :param route: маршрут согласования.
    :param default_deadline: нормативный срок исполнения по умолчанию (дней).
    """
    first_phase = route.phases.order_by('number').first()
    if not first_phase:
        raise ApplicationLogicException('В маршруте нет этапов.')

    if get_route_state(route) != RouteState.WAITING:
        raise ApplicationLogicException(
            'Для запуска маршрут должен находится в состоянии '
            '"{}".'.format(ROUTE_STATE_NAMES[RouteState.WAITING])
        )

    first_phase.planned_date = add_working_days(
        date.today(), first_phase.deadline or default_deadline
    )
    first_phase.clean_and_save()

    route_phase_start.send(None, phase=first_phase)
    route_phase_change_state.send(
        sender=None,
        phase=first_phase,
        src_state=PhaseState.WAITING,
        dst_state=PhaseState.EXECUTING,
    )


@atomic
def reset_route(route: Route) -> NoReturn:
    """Сбрасывает маршрут согласования.

    Все результаты рассмотрения в журнале согласования помечаются как
    исторические (``actual = False``), а плановая и фактическая даты
    исполнения всех этапов маршрута удаляются.

    :param route: маршрут согласования.
    """
    current_state = get_route_state(route)
    if current_state not in RESETABLE_ROUTE_STATES:
        raise ApplicationLogicException(
            'Для запуска маршрут должен находится в одном из следующих '
            'состояний: {} (сейчас "{}")'.format(
                ', '.join(
                    f'"{ROUTE_STATE_NAMES[state]}"'
                    for state in RESETABLE_ROUTE_STATES
                ),
                ROUTE_STATE_NAMES[current_state]
            )
        )

    route.in_reset_process = True

    for phase in route.phases.filter(
        Q(planned_date__isnull=False) | Q(actual_date__isnull=False)
    ):
        phase.planned_date = None
        phase.actual_date = None
        phase.full_clean()
        phase.save(update_fields=('planned_date', 'actual_date'))

    for log_record in Log.objects.filter(
        approover__phase__route=route,
        actual=True,
    ).iterator():
        log_record.actual = False
        log_record.full_clean()
        log_record.save(update_fields=('actual',))

    route.in_reset_process = False


@atomic
def resume_route(route: Route, default_deadline: int = 1) -> NoReturn:
    """Возобновляет согласование объекта, возвращенного на доработку.

    Согласование начинается с этапа, на котором объект согласования был
    возвращён на доработку, согласование предыдущих этапов останется в силе.

    :param route: маршрут согласования.
    :param default_deadline: нормативный срок исполнения по умолчанию (дней).
    """
    if get_route_state(route) not in NEGATIVE_ROUTE_STATES:
        raise ApplicationLogicException(
            'Для запуска маршрут должен находится в одном из следующих '
            'состояний: ' + ', '.join(
                f'"{ROUTE_STATE_NAMES[state]}"'
                for state in NEGATIVE_ROUTE_STATES
            )
        )

    log_record = Log.objects.filter(
        approover__phase__route=route,
        actual=True,
        result__in=(
            ReviewResult.NEED_CHANGES,
            ReviewResult.REJECTED,
        ),
    ).order_by('approover__phase__number').first()

    for phase in RoutePhase.objects.filter(
        route_id=log_record.approover.phase.route_id,
        number__gte=log_record.approover.phase.number,
    ).order_by('-number'):
        if phase == log_record.approover.phase:
            phase.planned_date = add_working_days(
                date.today(), phase.deadline or default_deadline
            )
        else:
            phase.planned_date = None
        phase.actual_date = None
        phase.full_clean()
        phase.save(update_fields=('planned_date', 'actual_date'))

    for log_record in Log.objects.filter(
        approover__phase__route=route,
        approover__phase__number__gte=log_record.approover.phase.number,
        actual=True,
    ):
        log_record.actual = False
        log_record.full_clean()
        log_record.save(update_fields=('actual',))


def get_approover_types_for(
    object_type: ContentType,
) -> Generator[Tuple[ContentType, ActionPack], None, None]:
    """Возвращает типы согласующих и паки выбора для объектов указанного типа.

    :param object_type: тип объектов.
    """
    config = m3_object_coordination.config

    for content_type in ContentType.objects.all():
        model = content_type.model_class()
        if model and config.can_approove(object_type.model_class(), model):
            pack = config.get_approover_select_pack_for(model)
            yield content_type, pack
