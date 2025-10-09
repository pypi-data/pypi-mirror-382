# coding: utf-8
from builtins import staticmethod
from collections import defaultdict
from functools import lru_cache
from itertools import groupby
from operator import itemgetter
from typing import Iterable
from typing import List
from typing import NoReturn
from typing import Union
import json

from django.contrib.contenttypes.models import ContentType
from django.db.models.base import Model
from django.db.transaction import atomic
from m3.actions.exceptions import ApplicationLogicException
from m3.actions.results import OperationResult
from m3.actions.results import PreJsonResult
from m3_ext.ui.results import ExtUIScriptResult
from objectpack.actions import BaseAction
from objectpack.actions import BasePack
from objectpack.actions import ObjectPack

from m3_object_coordination._external_utils.m3 import (
    convert_validation_error_to)
import m3_object_coordination

from .components import ApprooverEditWindow
from .components import PhaseEditWindow
from .components import TemplateSelectWindow
from ...constants import ROUTE_STATE_NAMES
from ...constants import ContextParser
from ...constants import MoveDirection
from ...constants import PhaseState
from ...constants import RouteState
from ...models import Log
from ...models import Route
from ...models import RouteApproover
from ...models import RoutePhase
from ...models import RouteTemplate
from ...ui import ApprooverType
from ...ui.base.actions import CheckApprooverSelectPacksMixin
from ...ui.routes.components import HistoryWindow
from ...ui.routes.components import ReviewWindow
from ...utils import create_route_for
from ...utils import get_phase_state
from ...utils import get_route_state
from ...utils import move_phases
from ...utils import set_review_result
from ...utils import start_route


# -----------------------------------------------------------------------------


def _get_content_type(content_type_id: int) -> ContentType:
    try:
        result = ContentType.objects.get_for_id(content_type_id)
    except ContentType.DoesNotExist:
        raise ApplicationLogicException(
            'Тип объектов с указанным идентификатором '
            f'(id={content_type_id}) не существует.'
        )

    return result


def _get_route_template(template_id: int) -> RouteTemplate:
    try:
        result = RouteTemplate.objects.get(pk=template_id)
    except RouteTemplate.DoesNotExist:
        raise ApplicationLogicException(
            'Шаблон маршрута согласования с указанным идентификатором '
            f'(id={template_id}) не существует.'
        )

    return result


def get_route(route_id: int) -> Route:
    """Возвращает маршрут согласования по ID.

    :param route_id: ID маршрута.

    :raises m3.actions.exceptions.ApplicationLogicException:

      - если маршрут согласования по такому ID не найден.
    """
    try:
        result = Route.objects.prefetch_related(
            'phases__approovers__log_records',
        ).get(pk=route_id)
    except Route.DoesNotExist:
        raise ApplicationLogicException(
            'Маршрут согласования с указанным идентификатором '
            f'(id={route_id}) не существует.'
        )

    return result


def _get_phase(phase_id: int) -> RoutePhase:
    try:
        result = RoutePhase.objects.get(pk=phase_id)
    except RoutePhase.DoesNotExist:
        raise ApplicationLogicException(
            'Этап маршрут согласования с указанным идентификатором '
            f'(id={phase_id}) не существует.'
        )

    return result


def get_approover(approover_id: int) -> RouteApproover:
    """Возвращает согласующий объект по ID.

    :param approover_id: ID согласующего объекта.

    :raises m3.actions.exceptions.ApplicationLogicException:

      - если согласующий объект по такому ID не найден.
    """
    try:
        result = RouteApproover.objects.get(pk=approover_id)
    except RouteApproover.DoesNotExist:
        raise ApplicationLogicException(
            f'Согласующий с указанным идентификатором (id={approover_id}) не '
            'существует.'
        )

    return result


def _get_object(
    content_type: Union[int, ContentType],
    object_id: int,
) -> Model:
    if isinstance(content_type, int):
        content_type = _get_content_type(content_type)
    model = content_type.model_class()

    try:
        result = model.objects.get(pk=object_id)
    except model.DoesNotExist:
        raise ApplicationLogicException(
            f'{model._meta.verbose_name} с указанным идентификатором '
            f'(id={object_id}) не существует.'
        )

    return result


def _get_phase_state_str(phase: RoutePhase) -> str:
    if phase.state == PhaseState.EXECUTED:
        state_str = (
            'Исполнен ' + phase.actual_date.strftime('%d.%m.%Y')
        )

    elif phase.state == PhaseState.EXECUTING:
        if phase.planned_date:
            planned_date_str = phase.planned_date.strftime('%d.%m.%Y')
        else:
            planned_date_str = '<не указано>'
        state_str = 'Срок {} дн. до {}'.format(
            phase.deadline or '<не указано>', planned_date_str
        )

    elif phase.state == PhaseState.WAITING:
        state_str = 'Ожидание завершения предыдущего этапа'

    elif phase.state == PhaseState.BLOCKED:
        state_str = (
            'Заблокирован ' + phase.actual_date.strftime('%d.%m.%Y')
        )

    elif phase.state == PhaseState.STOPPED:
        state_str = (
            'Остановлен ' + phase.actual_date.strftime('%d.%m.%Y')
        )

    else:
        state_str = ''

    return f'Этап {phase.number}: {phase.name}. {state_str}'


def _connect_phases(phases: Iterable[RoutePhase]) -> NoReturn:
    """Заполнение связей между этапами согласования."""
    # pylint: disable=consider-using-enumerate
    last_index = len(phases) - 1
    for i in range(len(phases)):
        phases[i].is_first = i == 0
        phases[i].is_last = i == last_index

        phases[i].previous = None if phases[i].is_first else phases[i - 1]
        phases[i].next = None if phases[i].is_last else phases[i + 1]


class RouteDataAction(BaseAction):

    """Обработчик запроса данных для грида маршрута согласования."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()

        result.update(
            route_id=dict(type=ContextParser.INT_OR_NONE, default=None),
        )

        return result

    @staticmethod
    def _get_actions_permitted_for_route(route):
        """Возвращает перечень разрешенных действий над маршрутом ."""
        result = []

        if get_route_state(route) in (RouteState.PREPARATION,
                                      RouteState.WAITING):
            result.extend((
                # Добавление этапа согласования в маршрут.
                'add-phase',
                # Пересоздание маршрута на основе другого шаблона.
                'change-template',
            ))

        return result

    @staticmethod
    def _get_actions_permitted_for_phase(phase):
        assert 'approovers' in getattr(phase, '_prefetched_objects_cache')

        result = []

        if get_route_state(phase.route) in (RouteState.PREPARATION,
                                            RouteState.WAITING):
            result.extend((
                'edit-phase',  # Изменение этапа согласования.
                'add-approover',  # Добавление согласующего в этап.
                'delete-phase',  # Удаление этапа согласования из маршрута.
            ))
            if not phase.is_first:
                result.append('move-phase-up')
            if not phase.is_last:
                result.append('move-phase-down')

        return result

    @staticmethod
    def _get_actions_permitted_for_approover(
        phase: RoutePhase,
        route_approover: RouteApproover,
        user: Model
    ) -> List[str]:
        config = m3_object_coordination.config

        result = [
            'view-approover-history'  # Просмотр истории рассмотрения.
        ]

        if get_route_state(phase.route) in (RouteState.PREPARATION,
                                            RouteState.WAITING):
            result.extend((
                'delete-approover',  # Удаление согласующего из этапа.
            ))

        route_object = phase.route.object
        approover_object = route_approover.approover
        phase_state = get_phase_state(phase)
        if (
            phase_state == PhaseState.EXECUTING and
            config.can_approove(route_object, approover_object) and
            config.can_approove_as(user, approover_object)
        ):
            result.append(
                'set-review-result'  # Проставление результата рассмотрения.
            )

        if (
            # Состояние этапа: "Исполняемый".
            phase_state == PhaseState.EXECUTING and

            # Пользователь относится к подразделению, согласующему данный этап.
            m3_object_coordination.config.can_approove_as(
                user, route_approover.approover
            ) and

            # Этап еще не согласован подразделением пользователя.
            not Log.objects.filter(
                approover=route_approover,
                actual=True,
            ).exists()
        ):
            result.extend((
                'approve',  # Согласование.
                'need-changes',  # Отправка на доработку.
                'reject',  # Отклонение.
            ))

        return result

    @staticmethod
    def _prepare_approovers(phases):
        assert all(
            'approovers' in getattr(phase, '_prefetched_objects_cache')
            for phase in phases
        )

        approovers = {
            approover.id: approover
            for phase in phases
            for approover in phase.approovers.all()
        }

        log_query = Log.objects.filter(
            actual=True,
            approover__in=approovers.values(),
        ).order_by('approover', 'timestamp')
        log_by_approover = {
            approovers[approover_id]: tuple(log_records)
            for approover_id, log_records in groupby(
                log_query,
                lambda l: l.approover_id
            )
        }
        for approover in approovers.values():
            if approover not in log_by_approover:
                log_by_approover[approover] = None

        config = m3_object_coordination.config
        for approover, log_records in log_by_approover.items():
            # Формирование значений для столбцов "Решение", "Комментарий",
            # "Пользователь" и "Дата".
            if log_records:
                approover.log_result = log_records[0].get_result_display()
                approover.log_comment = log_records[0].comment
                approover.log_user = config.get_user_repr(log_records[0].user)
                approover.log_timestamp = (
                    log_records[0].timestamp.strftime('%d.%m.%Y %H:%M:%S')
                )
            else:
                approover.log_result = ''
                approover.log_comment = ''
                approover.log_user = None
                approover.log_timestamp = ''

    def _get_approover_data(self, phase, approover, user):
        config = m3_object_coordination.config

        return dict(
            id=approover.id,
            title=config.get_approover_repr(approover.approover),
            permitted_actions=json.dumps(
                self._get_actions_permitted_for_approover(
                    phase, approover, user
                )
            ),
            result=approover.log_result,
            comment=approover.log_comment,
            user=config.get_user_repr(approover.log_user),
            time=approover.log_timestamp,
        )

    def _get_phase_data(self, phase, user):
        assert 'approovers' in getattr(phase, '_prefetched_objects_cache')

        return dict(
            id=phase.id,
            title=phase.title,
            permitted_actions=json.dumps(
                self._get_actions_permitted_for_phase(phase)
            ),
            approovers=tuple(
                self._get_approover_data(phase, approover, user)
                for approover in phase.approovers.all()
            ),
        )

    def _get_phases_data(self, route, user):
        phases = tuple(
            route.phases.prefetch_related(
                'approovers',
            ).order_by('number')
        )

        _connect_phases(phases)
        for phase in phases:
            phase.state = get_phase_state(phase)
            if route.state in (RouteState.PREPARATION, RouteState.WAITING):
                phase.title = f'Этап {phase.number}: {phase.name}'
            else:
                phase.title = _get_phase_state_str(phase)

        self._prepare_approovers(phases)

        return [
            self._get_phase_data(phase, user)
            for phase in phases
        ]

    def _get_route_data(self, route, user):
        phases_data = self._get_phases_data(route, user)
        permitted_actions = self._get_actions_permitted_for_route(route)

        result = dict(
            id=route.id,
            state_id=int(route.state),
            state_name=ROUTE_STATE_NAMES[route.state],
            permitted_actions=permitted_actions,
            phases=phases_data,
        )
        if route.template:
            result['template_id'] = route.template_id
            result['template_title'] = str(route.template)

        return result

    def run(self, request, context):  # noqa: D102
        config = m3_object_coordination.config
        current_user = config.get_current_user(request)

        route = get_route(context.route_id)
        route.state = get_route_state(route)

        return PreJsonResult(dict(
            route=self._get_route_data(route, current_user),
        ))


class PhaseAddWindowAction(BaseAction):

    """Отображение окна добавления этапа согласования в маршрут."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()
        result.update(
            route_id=dict(type='int'),
        )
        return result

    def run(self, request, context):  # noqa: D102
        win = PhaseEditWindow()
        win.set_params(dict(
            title='{}: Добавление'.format(RoutePhase._meta.verbose_name),
            form_url=self.parent.phase_add_action.get_absolute_url(),
        ))
        return ExtUIScriptResult(win, context)


class PhaseAddAction(BaseAction):

    """Добавление этапа согласования в маршрут."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()
        result.update(
            route_id=dict(type='int'),
            name=dict(type='str'),
            deadline=dict(type=ContextParser.INT_OR_NONE, default=None),
        )
        return result

    @convert_validation_error_to(ApplicationLogicException)
    def run(self, request, context):  # noqa: D102
        route = get_route(context.route_id)

        RoutePhase.objects.create(
            route=route,
            name=context.name,
            deadline=context.deadline,
        )

        return OperationResult()


class PhaseEditWindowAction(BaseAction):

    """Отображение окна редактирования этапа согласования."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()
        result.update(
            phase_id=dict(type='int'),
        )
        return result

    def run(self, request, context):  # noqa: D102
        phase = _get_phase(context.phase_id)

        win = PhaseEditWindow()
        win.set_params(dict(
            title='{}: Редактирование'.format(RoutePhase._meta.verbose_name),
            form_url=self.parent.phase_edit_action.get_absolute_url(),
            phase=phase,
        ))
        return ExtUIScriptResult(win, context)


class PhaseEditAction(BaseAction):

    """Редактирование этапа согласования."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()
        result.update(
            phase_id=dict(type='int'),
            name=dict(type='str'),
            deadline=dict(type=ContextParser.INT_OR_NONE, default=None),
        )
        return result

    @convert_validation_error_to(ApplicationLogicException)
    def run(self, request, context):  # noqa: D102
        phase = _get_phase(context.phase_id)
        phase.name = context.name
        phase.deadline = context.deadline
        phase.clean_and_save()

        return OperationResult()


class PhaseDeleteAction(BaseAction):

    """Удаление этапа со всеми согласующими в нём."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()
        result.update(
            phase_id=dict(type='int'),
        )
        return result

    @atomic
    def run(self, request, context):  # noqa: D102
        phase = _get_phase(context.phase_id)

        if get_route_state(phase.route) not in (
            RouteState.PREPARATION,
            RouteState.WAITING,
        ):
            raise ApplicationLogicException(
                'Удаление этапа согласования допустимо только из маршрутов в '
                'состояниях "{}" или "{}".'.format(
                    ROUTE_STATE_NAMES[RouteState.PREPARATION],
                    ROUTE_STATE_NAMES[RouteState.WAITING],
                )
            )

        phase.approovers.all().delete()

        phase.safe_delete()

        return OperationResult()
# -----------------------------------------------------------------------------


class ApprooverTypePack(CheckApprooverSelectPacksMixin,
                        ObjectPack):

    """Пак для полей выбора типа согласующего."""

    model = ApprooverType
    _is_primary_for_model = False

    columns = (
        dict(
            data_index='name',
            header='Тип объекта',
        ),
        dict(
            data_index='column_name_on_select',
            hidden=True,
        ),
        dict(
            data_index='select_window_url',
            hidden=True,
        ),
    )
    column_name_on_select = 'name'

    def declare_context(self, action):  # noqa: D102
        result = super().declare_context(action)

        result['phase_id'] = dict(type='int')

        return result

    def get_rows_query(self, request, context):  # noqa: D102
        phase = _get_phase(context.phase_id)

        return ApprooverType.objects.configure(
            object_type=ContentType.objects.get_for_id(
                phase.route.object_type_id
            )
        )

    def get_display_text(self, key, attr_name=None):  # noqa: D102
        if attr_name == 'name':
            content_type = ContentType.objects.get_for_id(key)
            result = content_type.name if content_type else None
        else:
            result = super().get_display_text(key, attr_name)

        return result


class ApprooverAddWindowAction(BaseAction):

    """Отображение окна добавления согласующего в этап."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()
        result.update(
            phase_id=dict(type='int'),
        )
        return result

    def run(self, request, context):  # noqa: D102
        phase = _get_phase(context.phase_id)

        win = ApprooverEditWindow()
        win.set_params(dict(
            create_new=True,
            title='{}: Добавление'.format(RouteApproover._meta.verbose_name),
            form_url=self.parent.approover_add_action.get_absolute_url(),
            phase=phase,
            template_id_param_name=(
                self.parent.approover_type_pack.id_param_name
            ),
            select_url_action=(
                self.parent.approover_type_pack.select_window_action
            ),
        ))
        return ExtUIScriptResult(win, context)


class ApprooverAddAction(BaseAction):

    """Добавление согласующего в этап."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()
        result.update(
            phase_id=dict(type='int'),
            approover_type_id=dict(type='int'),
            approover_id=dict(type='int'),
        )
        return result

    @convert_validation_error_to(ApplicationLogicException)
    def run(self, request, context):  # noqa: D102
        phase = _get_phase(context.phase_id)
        approover_type = _get_content_type(context.approover_type_id)
        approover = _get_object(approover_type, context.approover_id)

        RouteApproover.objects.create(
            phase=phase,
            approover_type=approover_type,
            approover=approover,
        )

        return OperationResult()


class ApprooverDeleteAction(BaseAction):

    """Удаление согласующего."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()
        result.update(
            approover_id=dict(type='int'),
        )
        return result

    def run(self, request, context):  # noqa: D102
        approover = get_approover(context.approover_id)

        if get_route_state(approover.phase.route) not in (
            RouteState.PREPARATION,
            RouteState.WAITING,
        ):
            raise ApplicationLogicException(
                'Удаление согласующих допустимо только из маршрутов в '
                'состояниях "{}" или "{}".'.format(
                    ROUTE_STATE_NAMES[RouteState.PREPARATION],
                    ROUTE_STATE_NAMES[RouteState.WAITING],
                )
            )

        approover.safe_delete()

        return OperationResult()
# -----------------------------------------------------------------------------


class ReorderAction(BaseAction):

    """Изменение порядка этапов в шаблоне."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        return dict(
            phase_id=dict(type='int'),
            direction=dict(type='str'),
        )

    @convert_validation_error_to(ApplicationLogicException)
    def run(self, request, context):  # noqa: D102
        if context.direction == 'up':
            direction = MoveDirection.UP
        elif context.direction == 'down':
            direction = MoveDirection.DOWN
        else:
            return OperationResult.by_message(
                'Указано недопустимое направление перемещения: '
                f'{context.direction}.'
            )

        phase = _get_phase(context.phase_id)
        move_phases(direction, phase)

        return OperationResult()
# -----------------------------------------------------------------------------


class TemplateSelectWindowAction(BaseAction):

    """Окно выбора шаблона для пересоздания маршрута согласования."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()

        result.update(
            object_type_id=dict(type='int'),
            current_route_id=dict(type='int'),
        )

        return result

    def run(self, request, context):  # noqa: D102
        win = TemplateSelectWindow()
        win.set_params(dict(
            grid_data_url=(
                self.parent.template_data_action.get_absolute_url()
            ),
            route_change_url=(
                self.parent.recreate_route_action.get_absolute_url()
            ),
            object_type_id=context.object_type_id,
            current_route_id=context.current_route_id,
        ))
        return ExtUIScriptResult(win)


class TemplateDataAction(BaseAction):

    """Загрузка данных для грида в окне выбора шаблона маршрута."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        result = super().context_declaration()

        result.update(
            object_type_id=dict(type='int'),
            current_route_id=dict(type='int'),
        )

        return result

    @staticmethod
    def _get_route_template_data(route_template, current_route):
        return dict(
            id=route_template.id,
            default=route_template.default,
            name=route_template.name,
            start_date=route_template.start_date,
            end_date=route_template.end_date,
            current=(current_route.template_id == route_template.id)
        )

    def _get_rows_data(self, object_type, current_route):
        query = RouteTemplate.actual_objects.filter(
            object_type=object_type,
        )

        return [
            self._get_route_template_data(route_template, current_route)
            for route_template in query
        ]

    def run(self, request, context):  # noqa: D102
        object_type = _get_content_type(context.object_type_id)
        current_route = get_route(context.current_route_id)

        rows_data = self._get_rows_data(object_type, current_route)

        return PreJsonResult(dict(
            rows=rows_data,
            total=len(rows_data),
        ))


class RecreateRouteAction(BaseAction):

    """Пересоздание маршрута согласования на основе указанного шаблона."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102 pylint: disable=no-self-use
        result = super().context_declaration()

        result.update(
            object_type_id=dict(type='int'),
            object_id=dict(type='int'),
            template_id=dict(type='int'),
        )

        return result

    @staticmethod
    def _get_route_template(context):
        try:
            return RouteTemplate.objects.get(
                pk=context.route_template_id,
            )
        except RouteTemplate.DoesNotExist:
            raise ApplicationLogicException(
                'Указанный шаблон маршрута согласования '
                f'(id={context.route_template_id}) не существует.'
            )

    @convert_validation_error_to(ApplicationLogicException)
    @atomic
    def run(self, request, context):  # noqa: D102
        obj = _get_object(context.object_type_id, context.object_id)
        new_route_template = _get_route_template(context.template_id)

        new_route = create_route_for(obj, new_route_template)

        return PreJsonResult(dict(
            route_id=new_route.id,
        ))
# -----------------------------------------------------------------------------


class StartRouteAction(BaseAction):

    """Запуск маршрута согласования."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102 pylint: disable=no-self-use
        result = super().context_declaration()

        result.update(
            route_id=dict(type='int'),
            deadline=dict(type=ContextParser.INT_OR_NONE, default=10),
        )

        return result

    @convert_validation_error_to(ApplicationLogicException)
    def run(self, request, context):  # noqa: D102
        route = get_route(context.route_id)
        start_route(route, context.deadline)

        return OperationResult()
# -----------------------------------------------------------------------------


class HistoryWindowAction(BaseAction):

    """Отображение окна "История согласования"."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102 pylint: disable=no-self-use
        result = super().context_declaration()

        result.update(
            approover_id=dict(type='int'),
        )

        return result

    def run(self, request, context):  # noqa: D102
        win = HistoryWindow()
        win.set_params(dict(
            grid_data_url=(
                self.parent.history_data_action.get_absolute_url()
            ),
            approover_id=context.approover_id,
        ))
        return ExtUIScriptResult(win)


class HistoryDataAction(BaseAction):

    """Данные для грида "История согласования"."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102 pylint: disable=no-self-use
        result = super().context_declaration()

        result.update(
            approover_id=dict(type='int'),
        )

        return result

    @staticmethod
    def _get_content_types(data):
        return {
            content_type_id: ContentType.objects.get_for_id(content_type_id)
            for content_type_id in set(map(itemgetter('user_type_id'), data))
        }

    @staticmethod
    def _get_users(data):
        user_pks = defaultdict(list)
        for log_record_data in data:
            user_type_id = log_record_data['user_type_id']
            user_pks[user_type_id].append(log_record_data['user_id'])

        result = {}
        for user_type_id, primary_keys in user_pks.items():
            model = ContentType.objects.get_for_id(user_type_id).model_class()
            for user in model.objects.filter(pk__in=primary_keys):
                result[user_type_id, user.pk] = user

        return result

    @staticmethod
    def _get_data(approover: RouteApproover):
        result = []
        for log_record in approover.log_records.all():
            result.append(dict(
                user_type_id=log_record.user_type_id,
                user_id=log_record.user_id,
                result=log_record.get_result_display(),
                timestamp=log_record.timestamp,
                comment=log_record.comment,
                actual=log_record.actual,
            ))

        content_types = HistoryDataAction._get_content_types(result)
        users = HistoryDataAction._get_users(result)
        for log_record_data in result:
            user_type_id = log_record_data['user_type_id']
            user_type = content_types[user_type_id]
            user_id = log_record_data['user_id']
            user = users[user_type_id, user_id]
            log_record_data.update(
                user_type=user_type.name,
                user_repr=m3_object_coordination.config.get_user_repr(user),
            )

        return sorted(result, key=itemgetter('timestamp'))

    def run(self, request, context):  # noqa: D102
        approover = get_approover(context.approover_id)
        data = self._get_data(approover)

        return PreJsonResult(dict(
            rows=data,
            total=len(data),
        ))
# -----------------------------------------------------------------------------


def _check_review_access(approover: RouteApproover, user: Model):
    """Проверка доступности действия над согласуемым объектом.

    :param approover: согласующий объект, (например, отдел организации).
    :param user: пользователь, просматривающий объект согласования.
    :return:

    :raises m3.actions.exceptions.ApplicationLogicException:

        - если действие не доступно для согласуемого объекта;
        - если согласующий объект не имеет доступ к действию согласования.
    """
    config = m3_object_coordination.config

    if not config.can_approove(
        approover.phase.route.object, approover.approover
    ):
        raise ApplicationLogicException(
            'Согласование "{}" недоступно для "{}".'
            .format(
                config.get_object_repr(approover.phase.route.object),
                config.get_user_repr(user),
            )
        )

    if not config.can_approove_as(user, approover.approover):
        raise ApplicationLogicException(
            'Вам недоступно согласование от имени "{}".'
            .format(config.get_approover_repr(approover.approover))
        )


class ReviewWindowAction(BaseAction):

    """Отображение окна проставления результата рассмотрения."""

    @staticmethod
    def _get_window():
        """Возвращает окно проставления результата."""
        return ReviewWindow()

    def _get_window_params(self, config, approover, context):
        """Возвращает параметры настройки окна."""
        # pylint: disable=unused-argument
        return dict(
            form_url=self.parent.set_review_result_action.get_absolute_url(),
            create_new=True,
            title='Проставление результата рассмотрения',
            object_repr=config.get_object_repr(approover.phase.route.object),
            phase_name=approover.phase.name,
            approover_id=approover.id,
            approover_repr=config.get_approover_repr(approover),
        )

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        return dict(
            route_approover_id=dict(type='int'),
        )

    def run(self, request, context):  # noqa: D102
        config = m3_object_coordination.config

        approover: RouteApproover = get_approover(context.route_approover_id)
        current_user: Model = config.get_current_user(request)

        _check_review_access(approover, current_user)

        win = self._get_window()
        win.set_params(self._get_window_params(config, approover, context))

        return ExtUIScriptResult(win, context)


class SetReviewResultAction(BaseAction):

    """Сохранение результата рассмотрения объекта согласования."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        return dict(
            route_approover_id=dict(type='int'),
            result=dict(type='int'),
            comment=dict(type='str_or_none', default=None),
        )

    @convert_validation_error_to(ApplicationLogicException)
    def run(self, request, context):  # noqa: D102
        config = m3_object_coordination.config

        approover: RouteApproover = get_approover(context.route_approover_id)
        current_user: Model = config.get_current_user(request)

        _check_review_access(approover, current_user)

        set_review_result(
            approover=approover,
            result=context.result,
            comment=context.comment,
            user=current_user,
        )

        return OperationResult()
# -----------------------------------------------------------------------------


class Pack(BasePack):

    """Набор обработчиков действия для грида маршрута согласования."""

    def __init__(self):  # noqa: D107
        super().__init__()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.route_data_action = RouteDataAction()

        self.phase_add_window_action = PhaseAddWindowAction()
        self.phase_add_action = PhaseAddAction()
        self.phase_edit_window_action = PhaseEditWindowAction()
        self.phase_edit_action = PhaseEditAction()
        self.phase_delete_action = PhaseDeleteAction()

        self.approover_add_window_action = ApprooverAddWindowAction()
        self.approover_add_action = ApprooverAddAction()
        self.approover_delete_action = ApprooverDeleteAction()

        self.reorder_action = ReorderAction()

        self.template_select_window_action = TemplateSelectWindowAction()
        self.template_data_action = TemplateDataAction()
        self.recreate_route_action = RecreateRouteAction()

        self.start_route_action = StartRouteAction()

        self.review_window_action = ReviewWindowAction()
        self.set_review_result_action = SetReviewResultAction()

        self.history_window_action = HistoryWindowAction()
        self.history_data_action = HistoryDataAction()

        self.actions.extend((
            self.route_data_action,
            self.phase_add_window_action,
            self.phase_add_action,
            self.phase_edit_window_action,
            self.phase_edit_action,
            self.phase_delete_action,

            self.approover_add_window_action,
            self.approover_add_action,
            self.approover_delete_action,

            self.reorder_action,

            self.template_select_window_action,
            self.template_data_action,
            self.recreate_route_action,

            self.start_route_action,

            self.review_window_action,
            self.set_review_result_action,

            self.history_window_action,
            self.history_data_action,
        ))
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.approover_type_pack = ApprooverTypePack()

        self.subpacks.extend((
            self.approover_type_pack,
        ))
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
