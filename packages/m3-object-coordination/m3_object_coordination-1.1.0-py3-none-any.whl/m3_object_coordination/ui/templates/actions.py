# coding: utf-8
from functools import lru_cache
from operator import itemgetter

from django.contrib.contenttypes.models import ContentType
from django.db.models import CharField
from django.db.models.expressions import Case
from django.db.models.expressions import Func
from django.db.models.expressions import Value
from django.db.models.expressions import When
from django.db.transaction import atomic
from django.utils.functional import SimpleLazyObject
from m3.actions import ControllerCache
from m3.actions.exceptions import ApplicationLogicException
from m3.actions.results import OperationResult
from objectpack.actions import BaseAction
from objectpack.actions import ObjectPack
from objectpack.filters import ColumnFilterEngine
from objectpack.filters import FilterByField
from objectpack.models import VirtualModel
from objectpack.slave_object_pack.actions import SlavePack

import m3_object_coordination

from .components import ApprooverEditWindow
from .components import ListWindow
from .components import PhaseEditWindow
from .components import TemplateEditWindow
from .. import ApprooverType
from ..base.actions import CheckApprooverSelectPacksMixin
from ..._external_utils.m3 import PackValidationMixin
from ..._external_utils.m3 import convert_validation_error_to
from ..._external_utils.utils.misc import cached_property
from ...constants import ContextParser
from ...constants import MoveDirection
from ...models import Route
from ...models import RouteApproover
from ...models import RoutePhase
from ...models import RouteTemplate
from ...models import RouteTemplateApproover
from ...models import RouteTemplatePhase
from ...utils import move_phases


# -----------------------------------------------------------------------------


class ObjectType(VirtualModel):

    """Виртуальная модель с наименованиями типов объектов согласования."""

    def __init__(self, data):  # noqa: D107
        self.id = data['id']
        self.name = data['name']

    @classmethod
    def _get_ids(cls):
        config = m3_object_coordination.config

        data = []
        for content_type in ContentType.objects.all():
            model = content_type.model_class()
            if model and config.can_coordinate(model):
                data.append(
                    dict(
                        id=content_type.id,
                        name=content_type.name,
                    )
                )

        return sorted(data, key=itemgetter('name'))


class ObjectTypePack(ObjectPack):

    """Пак для полей выбора типа объектов согласования."""

    model = ObjectType
    _is_primary_for_model = False

    columns = (
        dict(
            data_index='name',
            header='Тип объекта',
        ),
    )
    column_name_on_select = 'name'
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

        result[self.parent.phases_pack.id_param_name] = dict(type='int')

        return result

    def get_rows_query(self, request, context):  # noqa: D102
        phase_id = getattr(context, self.parent.phases_pack.id_param_name)

        phase = RouteTemplatePhase.objects.filter(pk=phase_id).first()
        if not phase:
            raise ApplicationLogicException(
                f'Указанный этап (id={phase_id}) не существует.'
            )

        return ApprooverType.objects.configure(
            object_type=ContentType.objects.get_for_id(
                phase.template.object_type_id
            )
        )

    def get_display_text(self, key, attr_name=None):  # noqa: D102
        if attr_name == 'name':
            content_type = ContentType.objects.get_for_id(key)
            result = content_type.name if content_type else None
        else:
            result = super().get_display_text(key, attr_name)

        return result
# -----------------------------------------------------------------------------


class ReorderAction(BaseAction):

    """Изменение порядка этапов в шаблоне."""

    @lru_cache(maxsize=1)
    def context_declaration(self):  # noqa: D102
        return {
            self.parent.id_param_name: dict(
                type=ContextParser.INT_TUPLE,
            ),
            'direction': dict(type='str'),
        }

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

        move_phases(
            direction,
            *RouteTemplatePhase.objects.filter(
                pk__in=getattr(context, self.parent.id_param_name),
            ).order_by('number')
        )

        return OperationResult()


class PhasesPack(PackValidationMixin, SlavePack):

    """Пак для грида "Этапы шаблона маршрута"."""

    model = RouteTemplatePhase

    columns = (
        dict(
            data_index='number',
            header='Порядковый номер',
            width=115,
            fixed=True,
            sortable=True,
        ),
        dict(
            data_index='name',
            header='Наименование',
            sortable=True,
        ),
        dict(
            data_index='deadline',
            header='Нормативный срок исполнения',
            width=175,
            fixed=True,
            sortable=True,
        )
    )
    column_name_on_select = 'name'
    allow_paging = False
    list_sort_order = ('number',)

    add_window = edit_window = PhaseEditWindow

    @cached_property
    def _parents(self):  # noqa: D102
        return (
            (self.parent.id_param_name, 'template'),
        )

    def __init__(self):  # noqa: D107
        super().__init__()

        self.reorder_action = ReorderAction()
        self.actions.extend((
            self.reorder_action,
        ))

    @atomic
    def delete_row(self, obj_id, request, context):  # noqa: D102
        for phase in RoutePhase.objects.filter(
            template=obj_id,
        ).iterator():
            phase.template = None
            phase.full_clean()
            phase.save(update_fields=('template',))

        for approover in RouteTemplateApproover.objects.filter(
            phase=obj_id,
        ).iterator():
            approover.safe_delete()

        super().delete_row(obj_id, request, context)
# -----------------------------------------------------------------------------


class ApprooversPack(PackValidationMixin, SlavePack):

    """Пак для грида "Согласующие на этапе"."""

    model = RouteTemplateApproover

    columns = (
        dict(
            data_index='approover_type.name',
            header='Тип согласующего',
            width=1,
        ),
        dict(
            data_index='approover_representation',
            header='Согласующий',
            width=2,
        ),
    )
    allow_paging = False

    add_window = edit_window = ApprooverEditWindow

    @cached_property
    def _parents(self):  # noqa: D102
        return (
            (self.parent.phases_pack.id_param_name, 'phase'),
        )

    def prepare_row(self, obj, request, context):  # noqa: D102
        obj = super().prepare_row(obj, request, context)

        config = m3_object_coordination.config
        obj.approover_representation = config.get_approover_repr(obj.approover)

        return obj

    def get_edit_window_params(self, params, request, context):  # noqa: D102
        params = super().get_edit_window_params(params, request, context)

        params['template_id_param_name'] = self.parent.id_param_name
        params['phase'] = RouteTemplatePhase.objects.filter(
            pk=getattr(context, self.parent.phases_pack.id_param_name),
        ).first()
        params['select_url_action'] = self.select_window_action

        return params

    def delete_row(self, obj_id, request, context):  # noqa: D102
        for approover in RouteApproover.objects.filter(
            template=obj_id,
        ).iterator():
            approover.template = None
            approover.full_clean()
            approover.save(update_fields=('template',))

        super().delete_row(obj_id, request, context)
# -----------------------------------------------------------------------------


class Pack(PackValidationMixin, ObjectPack):

    """Пак для шаблонов маршрутов согласования."""

    model = RouteTemplate

    allow_paging = False

    filter_engine_clz = ColumnFilterEngine
    columns = (
        dict(
            data_index='object_type_id',
            hidden=True,
        ),
        dict(
            data_index='object_type.name',
            header='Тип объекта',
            width=1,
            sortable=True,
            searchable=True,
            search_fields=(
                'object_type_name',
            ),
            filter=FilterByField(
                model,
                'object_type',
                lookup='object_type_id',
                model_register={
                    'ContentType': SimpleLazyObject(
                        lambda: ControllerCache.find_pack(
                            f'{__package__}.actions.ObjectTypePack'
                        )
                    ),
                },
                hide_trigger=False,
                hide_dict_select_trigger=True,
            ),
        ),
        dict(
            data_index='default',
            header='Шаблон по умолчанию',
            width=130,
            fixed=True,
            column_renderer='yesOrEmpty',
            sortable=True,
        ),
        dict(
            data_index='name',
            header='Наименование',
            width=3,
            sortable=True,
            searchable=True,
            filter=FilterByField(
                model,
                'name',
            ),
        ),
        dict(
            data_index='interval_range_str',
            header='Период действия',
            width=150,
            fixed=True,
            sortable=True,
            sort_fields=('start_date', 'end_date'),
            searchable=True,
            search_fields=('start_date_str', 'end_date_str'),
        ),
    )

    list_window = ListWindow
    add_window = edit_window = TemplateEditWindow

    def __init__(self):  # noqa: D107
        super().__init__()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.object_type_pack = ObjectTypePack()
        self.approover_type_pack = ApprooverTypePack()
        self.phases_pack = PhasesPack()
        self.approovers_pack = ApprooversPack()
        self.subpacks.extend((
            self.object_type_pack,
            self.approover_type_pack,
            self.phases_pack,
            self.approovers_pack,
        ))
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def extend_desktop(self, menu):
        """Добавляет ярлык на рабочий стол.

        По умолчанию ничего не делает, при необходимости расширяется в
        использующем подсистему согласования проекте.
        """

    def extend_menu(self, menu):
        """Добавляет пункт в главное меню.

        По умолчанию ничего не делает, при необходимости расширяется в
        использующем подсистему согласования проекте.
        """

    def get_list_window_params(self, params, request, context):  # noqa: D102
        params = super().get_list_window_params(params, request, context)

        del params['pack']
        params['templates_pack'] = self
        params['object_type_pack'] = self.object_type_pack
        params['phases_pack'] = self.phases_pack
        params['approovers_pack'] = self.approovers_pack
        params['reorder_phases_url'] = (
            self.phases_pack.reorder_action.get_absolute_url()
        )

        return params

    def get_rows_query(self, request, context):  # noqa: D102
        result = super().get_rows_query(request, context)

        if 'filter' in request.POST:
            # Добавление столбца "Тип объекта" в запрос для поиска и сортировки
            result = result.annotate(
                object_type_name=Case(
                    default=None,
                    output_field=CharField(),
                    *(
                        When(
                            object_type_id=content_type.id,
                            then=Value(content_type.name),
                        )
                        for content_type in ContentType.objects.iterator()
                    )
                ),
                start_date_str=Func(
                    'start_date',
                    template='to_char(%(expressions)s, \'DD.MM.YYYY\')',
                    output_field=CharField(),
                ),
                end_date_str=Func(
                    'end_date',
                    template='to_char(%(expressions)s, \'DD.MM.YYYY\')',
                    output_field=CharField(),
                ),
            )

        return result

    def prepare_row(self, obj, request, context):  # noqa: D102
        obj = super().prepare_row(obj, request, context)

        # select_related и prefetch_related не используются, т.к.
        # менеджер модели ContentType испольует кеширование.
        obj.object_type = ContentType.objects.get_for_id(obj.object_type_id)

        return obj

    @atomic
    def delete_row(self, obj_id, request, context):  # noqa: D102
        for route in Route.objects.filter(
            template=obj_id,
        ).iterator():
            route.template = None
            route.full_clean()
            route.save(update_fields=('template',))

        for approover in RouteTemplateApproover.objects.filter(
            phase__template=obj_id,
        ).iterator():
            approover.safe_delete()

        for phase in RouteTemplatePhase.objects.filter(
            template=obj_id,
        ).iterator():
            phase.safe_delete()

        super().delete_row(obj_id, request, context)
# -----------------------------------------------------------------------------
