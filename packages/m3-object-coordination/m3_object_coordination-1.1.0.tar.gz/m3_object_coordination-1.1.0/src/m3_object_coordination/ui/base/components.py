# coding: utf-8
from abc import ABCMeta
from abc import abstractmethod

from m3.actions.context import ActionContext
from m3_ext.ui.fields.complex import ExtDictSelectField
from m3_ext.ui.fields.simple import ExtStringField
from objectpack.ui import ModelEditWindow
from objectpack.ui import anchor100

from m3_object_coordination._external_utils.utils.misc import cached_property
from m3_object_coordination._external_utils.utils.ui import local_template
import m3_object_coordination


class ApprooverEditWindowBase(ModelEditWindow, metaclass=ABCMeta):

    """Окно добавления/редактирования согласующего подразделения на этапе."""

    @property
    @abstractmethod
    def model(self):  # noqa: D102
        pass

    @property
    @abstractmethod
    def _model_register(self):
        pass

    @cached_property
    def field_fabric_params(self):  # noqa: D102
        return dict(
            field_list=(
                'approover_type_id',
            ),
            model_register=self._model_register,
        )

    def __init__(self):  # noqa: D107
        super().__init__()

        self.get_select_action_url = None

    def _init_components(self):
        super()._init_components()

        self.field__phase_name = ExtStringField(
            label='Этап',
            read_only=True,
        )
        self.field__approover_id = ExtDictSelectField(
            name='approover_id',
            label='Согласующий',
        )

    def _do_layout(self):
        super()._do_layout()

        self.form.label_width = 110

        self.form.items[:] = map(anchor100, (
            self.field__phase_name,
            self.field__approover_type_id,
            self.field__approover_id,
        ))

    def set_params(self, params):  # noqa: D102
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Поле "Этап".

        phase = params['phase']
        template_id = phase.template_id
        id_param_name = params['template_id_param_name']

        self.action_context = self.action_context or ActionContext()
        setattr(self.action_context, id_param_name, template_id)
        self.field__phase_name.value = phase.name
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Поле "Тип согласующего".

        self.field__approover_type_id.hide_trigger = False
        self.field__approover_type_id.hide_dict_select_trigger = True
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Поле "Согласующий".

        self.field__approover_id.hide_dict_select_trigger = False
        if not params['create_new'] and params['object'].approover_type_id:
            obj = params['object']
            approover_model = obj.approover_type.model_class()
            config = m3_object_coordination.config
            pack = config.get_approover_select_pack_for(approover_model)
            self.field__approover_id.pack = pack.get_short_name()
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        self.template_globals = [
            local_template('approover-edit-window.js'),
        ]
        self.get_select_action_url = (
            params['select_url_action'].get_absolute_url()
        )

        super().set_params(params)
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
