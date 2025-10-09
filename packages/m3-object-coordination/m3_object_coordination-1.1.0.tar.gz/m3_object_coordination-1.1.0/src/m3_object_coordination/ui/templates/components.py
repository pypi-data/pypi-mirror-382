# coding: utf-8
from m3.actions import ControllerCache
from m3_ext.ui.containers.base import BaseExtContainer
from m3_ext.ui.containers.containers import ExtContainer
from m3_ext.ui.controls.buttons import ExtButton
from m3_ext.ui.panels.grids import ExtObjectGrid
from objectpack.ui import BaseWindow
from objectpack.ui import ModelEditWindow

from m3_object_coordination._external_utils.utils.misc import cached_property
from m3_object_coordination._external_utils.utils.ui import local_template

from ..base.components import ApprooverEditWindowBase
from ...models import RouteTemplate
from ...models import RouteTemplateApproover
from ...models import RouteTemplatePhase


class ListWindow(BaseWindow):

    """Окно просмотра шаблонов маршрутов согласования."""

    def __init__(self):  # noqa: D107
        super().__init__()

        self.reorder_phases_url = None
        self.get_select_action_url = None

    def _init_components(self):
        super()._init_components()

        self.grid__templates = ExtObjectGrid(
            cls='word-wrap-grid',
        )

        self.grid__phases = ExtObjectGrid(
            header=True,
            title='Этапы шаблона маршрута',
            cls='word-wrap-grid',
            style={
                'border-right': 'solid 1px #ccc',
            },
        )

        self.grid__approovers = ExtObjectGrid(
            header=True,
            title='Согласующие на этапе',
            cls='word-wrap-grid',
        )

        self.bottom_container = ExtContainer()

        self.grid__phases.top_bar.move_up_button = ExtButton(
            text='Переместить выше',
            handler='movePhasesUp',
            icon_cls='icon-arrow-up',
            disabled=True,
        )
        self.grid__phases.top_bar.move_down_button = ExtButton(
            text='Переместить ниже',
            handler='movePhasesDown',
            icon_cls='icon-arrow-down',
            disabled=True,
        )
        self.grid__phases.top_bar.items.extend((
            self.grid__phases.top_bar.move_up_button,
            self.grid__phases.top_bar.move_down_button,
        ))

    def _do_layout(self):
        super()._do_layout()

        self.layout = BaseExtContainer.VBOX
        self.layout_config['align'] = 'stretch'
        self.grid__templates.flex = 1
        self.bottom_container.flex = 1

        self.bottom_container.layout = BaseExtContainer.HBOX
        self.bottom_container.layout_config['align'] = 'stretch'
        self.grid__phases.flex = 1
        self.grid__approovers.flex = 1

        self.items[:] = (
            self.grid__templates,
            self.bottom_container,
        )
        self.bottom_container.items[:] = (
            self.grid__phases,
            self.grid__approovers,
        )

    def set_params(self, params):  # noqa: D102
        super().set_params(params)

        self.maximizable = self.maximized = True
        self.minimizable = True

        self.template_globals = [
            local_template('list-window.js'),
        ]

        params['templates_pack'].configure_grid(self.grid__templates)

        self.grid__phases.store.auto_load = False
        params['phases_pack'].configure_grid(self.grid__phases)

        self.grid__approovers.store.auto_load = False
        params['approovers_pack'].configure_grid(self.grid__approovers)
        self.get_select_action_url = (
            params['approovers_pack'].get_select_url()
        )

        self.reorder_phases_url = params['reorder_phases_url']


class TemplateEditWindow(ModelEditWindow):

    """Окно добавления/редактирования шаблона маршрута согласования."""

    model = RouteTemplate

    field_list = (
        'object_type_id',
        'default',
        'name',
        'start_date',
        'end_date',
    )

    @cached_property
    def field_fabric_params(self):  # noqa: D102
        return dict(
            field_list=self.field_list,
            keep_field_list_order=True,
            model_register={
                'ContentType': ControllerCache.find_pack(
                    f'{__package__}.actions.ObjectTypePack'
                )
            }
        )

    def set_params(self, params):  # noqa: D102
        super().set_params(params)

        self.width = 600
        self.form.label_width = 150
        self.template_globals = [
            local_template('template-edit-window.js')
        ]

        self.field__object_type_id.hide_trigger = False
        self.field__object_type_id.hide_dict_select_trigger = True


class PhaseEditWindow(ModelEditWindow):

    """Окно добавления/редактирования этапа шаблона маршрута."""

    model = RouteTemplatePhase

    field_list = (
        'name',
        'deadline',
    )
    field_fabric_params = dict(
        field_list=field_list,
    )

    def set_params(self, params):  # noqa: D102
        super().set_params(params)

        self.width = 500
        self.form.label_width = 140
        self.template_globals = [
            local_template('phase-edit-window.js'),
        ]


class ApprooverEditWindow(ApprooverEditWindowBase):

    """Окно добавления/редактирования согласующего подразделения на этапе."""

    model = RouteTemplateApproover

    @cached_property
    def _model_register(self):
        return {
            'ContentType': ControllerCache.find_pack(
                f'{__package__}.actions.ApprooverTypePack'
            ),
        }
