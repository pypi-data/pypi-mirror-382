# coding: utf-8
from m3.actions import ControllerCache
from m3_ext.ui.containers.containers import ExtToolBar
from m3_ext.ui.containers.containers import ExtToolbarMenu
from m3_ext.ui.containers.context_menu import ExtContextMenu
from m3_ext.ui.containers.context_menu import ExtContextMenuItem
from m3_ext.ui.containers.grids import ExtGridColumn
from m3_ext.ui.containers.grids import ExtGridRowSelModel
from m3_ext.ui.containers.trees import ExtTree
from m3_ext.ui.controls.buttons import ExtButton
from m3_ext.ui.fields.simple import ExtComboBox
from m3_ext.ui.fields.simple import ExtStringField
from m3_ext.ui.fields.simple import ExtTextArea
from m3_ext.ui.misc.store import ExtDataStore
from m3_ext.ui.panels.grids import ExtObjectGrid
from objectpack.ui import BaseEditWindow
from objectpack.ui import BaseWindow
from objectpack.ui import ModelEditWindow
from objectpack.ui import anchor100

from m3_object_coordination._external_utils.utils.misc import cached_property
from m3_object_coordination._external_utils.utils.ui import local_template

from ...constants import REVIEW_RESULT_NAMES
from ...constants import ReviewResult
from ...models import RouteApproover
from ...models import RoutePhase
from ...ui.base.components import ApprooverEditWindowBase


# -----------------------------------------------------------------------------


class RouteGridTopBar(ExtToolBar):

    """Верхняя панель с кнопками в гриде согласования."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(*args, **kwargs)

        self._ext_name = 'Ext.m3.ObjectCoordination.RouteGridTopBar'

        self.button__add_phase = ExtContextMenuItem(
            text='этап согласования',
            icon_cls='add_item',
        )
        self.button__add_approover = ExtContextMenuItem(
            text='согласующего',
            icon_cls='add_item',
        )
        menu = ExtContextMenu()
        menu.items[:] = (
            self.button__add_phase,
            self.button__add_approover,
        )
        self.menu__add = ExtToolbarMenu(
            icon_cls="add_item",
            menu=menu,
            text='Добавить...'
        )

        self.button__edit = ExtButton(
            text='Изменить',
            icon_cls='edit_item',
        )
        self.button__delete = ExtButton(
            text='Удалить',
            icon_cls='delete_item',
        )
        self.button__up = ExtButton(
            icon_cls='icon-arrow-up',
            tooltip_text='Переместить этап вверх',
        )
        self.button__down = ExtButton(
            icon_cls='icon-arrow-down',
            tooltip_text='Переместить этап вниз',
        )

        self.button__change_template = ExtButton(
            text='Пересоздать маршрут',
            icon_cls='icon-comment-edit',
        )

        self.button__refresh = ExtButton(
            text='Обновить',
            icon_cls='x-tbar-loading',
        )

        self.button__set_review_result = ExtButton(
            text='Указать результат рассмотрения',
            icon_cls='icon-pencil',
        )
        self.button__history = ExtButton(
            text='История',
            icon_cls='icon-book',
        )

    def render_base_config(self):  # noqa: D102
        super().render_base_config()

        put = self._put_config_value

        # Для того, чтобы каждая кнопка была под своим именем, добавляем их
        # вручную. Добавление их в список элементов контейнера осуществляется
        # на клиенте через itemIds.
        put('addMenu', self.menu__add.render)
        put('editButton', self.button__edit.render)
        put('deleteButton', self.button__delete.render)
        put('upButton', self.button__up.render)
        put('downButton', self.button__down.render)
        put('changeTemplateButton', self.button__change_template.render)
        put('refreshButton', self.button__refresh.render)
        put('setReviewResultButton', self.button__set_review_result.render)
        put('historyButton', self.button__history.render)


class DefaultActionUrl(property):

    """Свойство, с URL экшена по умолчанию.

    Возвращает URL экшена по умолчанию, если URL не был переопределен.
    """

    def __init__(self, attr: str, pack: str, action: str):
        """Инициализация свойства.

        :param attr: имя атрибута в классе.

        :param pack: имя класса (с пакетом) с набором обработчиков
            HTTP-запросов (:class:`~m3.action.ActionPack`).

        :param action: имя атрибута, в котором хранится обработчик
            HTTP-запросов (:class:`~m3.action.Action`)
        """
        super().__init__()

        self.attr = attr
        self.pack = pack
        self.action = action

    def __get__(self, instance, owner):  # noqa: D105
        if hasattr(instance, '_' + self.attr):
            result = getattr(instance, '_' + self.attr)
        else:
            pack = ControllerCache.find_pack(self.pack)
            assert pack, f'{self.pack} not registered.'
            action = getattr(pack, self.action)
            result = action.get_absolute_url()

        return result

    def __set__(self, instance, value):  # noqa: D105
        setattr(instance, '_' + self.attr)


class RoutePanel(ExtTree):

    """Грид с информацией о согласовании."""

    columns = [
        ExtGridColumn(
            header='Согласующий',
            data_index='title',
        ),
        ExtGridColumn(
            header='Решение',
            data_index='result',
        ),
        ExtGridColumn(
            header='Комментарий',
            data_index='comment',
        ),
        ExtGridColumn(
            header='Пользователь',
            data_index='user',
        ),
        ExtGridColumn(
            header='Дата',
            data_index='time',
        ),
    ]

    data_url = DefaultActionUrl(
        'data_url',
        __package__ + '.actions.Pack', 'route_data_action'
    )
    phase_add_window_url = DefaultActionUrl(
        'phase_add_window_url',
        __package__ + '.actions.Pack', 'phase_add_window_action'
    )
    phase_edit_window_url = DefaultActionUrl(
        'phase_edit_window_url',
        __package__ + '.actions.Pack', 'phase_edit_window_action'
    )
    phase_delete_url = DefaultActionUrl(
        'phase_delete_url',
        __package__ + '.actions.Pack', 'phase_delete_action'
    )
    approover_add_window_url = DefaultActionUrl(
        'approover_add_window_url',
        __package__ + '.actions.Pack', 'approover_add_window_action'
    )
    approover_delete_url = DefaultActionUrl(
        'approover_delete_url',
        __package__ + '.actions.Pack', 'approover_delete_action'
    )
    reorder_url = DefaultActionUrl(
        'reorder_url',
        __package__ + '.actions.Pack', 'reorder_action'
    )
    template_select_url = DefaultActionUrl(
        'template_select_url',
        __package__ + '.actions.Pack', 'template_select_window_action'
    )
    recreate_route_url = DefaultActionUrl(
        'recreate_route_url',
        __package__ + '.actions.Pack', 'recreate_route_action'
    )
    review_window_url = DefaultActionUrl(
        'review_window_url',
        __package__ + '.actions.Pack', 'review_window_action'
    )
    history_window_url = DefaultActionUrl(
        'history_window_url',
        __package__ + '.actions.Pack', 'history_window_action'
    )

    def __init__(self, *args, **kwargs):  # noqa: D107
        self.auto_load = True
        self.object_type_id = None
        self.object_id = None
        self.route_id = None
        self.__url = None

        super().__init__(*args, **kwargs)

        self._ext_name = 'Ext.m3.ObjectCoordination.RoutePanel'
        self.top_bar = RouteGridTopBar()

    def render_base_config(self):  # noqa: D102
        self._items = self.columns

        super().render_base_config()

        put = self._put_config_value

        put('autoLoad', self.auto_load)
        put('rootVisible', False)
        put('enableSort', False)
        put('useArrows', True)
        put('autoScroll', False)
        put('animate', True)
        put('containerScroll', True)

        put('objectTypeId', self.object_type_id)
        put('objectId', self.object_id)
        put('routeId', self.route_id)

        put('dataUrl', self.data_url)
        put('phaseAddWindowUrl', self.phase_add_window_url)
        put('phaseEditWindowUrl', self.phase_edit_window_url)
        put('phaseDeleteUrl', self.phase_delete_url)
        put('approoverAddWindowUrl', self.approover_add_window_url)
        put('approoverDeleteUrl', self.approover_delete_url)
        put('reorderUrl', self.reorder_url)
        put('templateSelectUrl', self.template_select_url)
        put('recreateRouteUrl', self.recreate_route_url)
        put('reviewWindowUrl', self.review_window_url)
        put('historyWindowUrl', self.history_window_url)

    def render(self):  # noqa: D102
        self.render_base_config()

        return 'new %s({%s})' % (self._ext_name, self._get_config_str())
# -----------------------------------------------------------------------------
# Окно добавления/редактирования этапа согласования.


class PhaseEditWindow(ModelEditWindow):

    """Окно редактирования этапа маршрута согласования."""

    model = RoutePhase
    field_list = (
        'name',
        'deadline',
    )
    field_fabric_params = dict(
        field_list=field_list,
        keep_field_list_order=True,
    )

    def set_params(self, params):  # noqa: D102
        super().set_params(params)

        self.template_globals = local_template('phase-edit-window.js')
        self.form.label_width = 130

        if 'phase' in params:
            self.form.from_object(params['phase'])
# -----------------------------------------------------------------------------
# Окно добавления/редактирования согласующего в этап.


class ApprooverEditWindow(ApprooverEditWindowBase):

    """Окно добавления/редактирования согласующего подразделения на этапе."""

    model = RouteApproover

    @cached_property
    def _model_register(self):
        return {
            'ContentType': ControllerCache.find_pack(
                f'{__package__}.actions.ApprooverTypePack'
            ),
        }
# -----------------------------------------------------------------------------
# Окно выбора маршрута согласования.


class TemplateSelectWindow(BaseWindow):

    """Окно выбора другого маршрута согласования."""

    def _init_components(self):
        super()._init_components()

        self.grid = ExtObjectGrid(
            cls='word-wrap-grid',
        )
        self.grid.sm = ExtGridRowSelModel(single_select=True)

        self.grid.add_column(
            data_index='default',
            header='Шаблон по умолчанию',
            width=1,
            column_renderer='yesNoRenderer',
        )
        self.grid.add_column(
            data_index='name',
            header='Наименование',
            width=3,
        )
        self.grid.add_column(
            data_index='start_date',
            header='Дата начала действия',
            fixed=True,
            width=130,
        )
        self.grid.add_column(
            data_index='end_date',
            header='Дата окончания действия',
            fixed=True,
            width=145,
        )

        self.button__select = ExtButton(
            text='Выбрать',
        )

    def _do_layout(self):
        super()._do_layout()

        self.layout = 'fit'
        self.items.append(self.grid)
        self.buttons.append(self.button__select)

    def set_params(self, params):  # noqa: D102
        super().set_params(params)

        self.read_only = True
        self.title = 'Шаблоны маршрутов согласования'
        self.height = 600
        self.width = 800
        self.template_globals = local_template('template-select-window.js')
        self.grid.cls = 'word-wrap-grid'

        self.object_type_id = params['object_type_id']
        self.current_route_id = params['current_route_id']
        self.grid.url_data = params['grid_data_url']
# -----------------------------------------------------------------------------
# Окно просмотра истории согласования.


class HistoryGrid(ExtObjectGrid):

    """Грид "История рассмотрения"."""

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(*args, **kwargs)

        self.cls = 'word-wrap-grid'

        self.add_column(
            data_index='timestamp',
            header='Дата',
            width=130,
            fixed=True,
        )
        self.add_column(
            data_index='result',
            header='Решение',
            width=90,
            fixed=True,
        )
        self.add_column(
            data_index='comment',
            header='Комментарий',
            width=2,
        )
        self.add_column(
            data_index='user_type',
            header='Тип пользователя',
            width=1,
        )
        self.add_column(
            data_index='user_repr',
            header='Пользователь',
            width=1,
        )


class HistoryWindow(BaseWindow):

    """Окно "История решений"."""

    def _init_components(self):
        super()._init_components()

        self.grid = HistoryGrid()

        self.button__close = ExtButton(
            text='Закрыть',
            handler='function(){win.close()}',
        )

    def _do_layout(self):
        super()._do_layout()

        self.title = 'История решений'
        self.layout = 'fit'
        self.width = 1300
        self.height = 600

        self.items[:] = (
            self.grid,
        )
        self.buttons[:] = (
            self.button__close,
        )

    def set_params(self, params):  # noqa: D102
        super().set_params(params)

        self.minimizable = self.maximizable = True

        self.grid.url_data = params['grid_data_url']
# -----------------------------------------------------------------------------


class ReviewWindow(BaseEditWindow):

    """Окно рассмотрения заявки."""

    def _init_components(self):
        super()._init_components()

        self.field__review_object = ExtStringField(
            label='Объект согласования',
            name='review_object',
            read_only=True,
        )
        self.field__phase = ExtStringField(
            label='Этап согласования',
            name='phase',
            read_only=True,
        )
        self.field__result = ExtComboBox(
            label='Результат',
            name='result',
            value_field='id',
            display_field='name',
            value=ReviewResult.AGREED.value,
            allow_blank=False,
            trigger_action=ExtComboBox.ALL,
        )
        self.field__result.store = ExtDataStore(REVIEW_RESULT_NAMES.items())
        self.field__comment = ExtTextArea(
            label='Комментарий',
            name='comment',
        )

    def _do_layout(self):
        super()._do_layout()

        self.height = 220
        self.resizable = False

        self.form.items[:] = map(anchor100, (
            self.field__review_object,
            self.field__phase,
            self.field__result,
            self.field__comment,
        ))

    def set_params(self, params):  # noqa: D102
        super().set_params(params)

        self.REVIEW_RESULT__AGREED = ReviewResult.AGREED.value

        self.template_globals = local_template('review-window.js')

        self.form.label_width = 130

        self.field__review_object.value = params['object_repr']
        self.field__phase.value = params['phase_name']

        current_action = params.get('current_action_id')
        if current_action is not None:
            # Если задано выполняемое действие, блокируем выпадающий список
            # "Результат" (оставляем только это действие)
            self.field__result.value = current_action
            self.field__result.default_text = (
                REVIEW_RESULT_NAMES[current_action]
            )
            self.field__result.read_only = True
# -----------------------------------------------------------------------------
