# coding: utf-8
from itertools import product

from django.apps.registry import apps
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import request_finished

import m3_object_coordination


class CheckApprooverSelectPacksMixin:

    """Класс-примесь к пакам выбора типа согласующего.

    Обеспечивает контроль корректности настройки окон выбора согласующих для
    всех настроенных типов согласующих.
    """

    def _check_approover_select_packs(self, **_):
        """Проверяет корректность настройки окон выбора.

        .. seealso::

           :meth:`~m3_object_coordination.IConfig.
               get_approover_select_pack_for`
        """
        request_finished.disconnect(self._check_approover_select_packs)

        config = m3_object_coordination.config
        for object_model, approover_model in product(
            apps.get_models(include_auto_created=True), repeat=2
        ):
            if (
                config.can_approove(object_model, approover_model) and
                not config.get_approover_select_pack_for(approover_model)
            ):
                raise ImproperlyConfigured(
                    f'Для модели "{approover_model._meta.verbose_name}" не '
                    'определен пак с окном выбора.'
                )

    def __init__(self):  # noqa: D107
        request_finished.connect(self._check_approover_select_packs)

        super().__init__()
