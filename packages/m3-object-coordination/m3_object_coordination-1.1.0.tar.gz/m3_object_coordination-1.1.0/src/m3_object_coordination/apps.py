# coding: utf-8
from django.apps import AppConfig as AppConfigBase
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import router

from m3_object_coordination._external_utils.utils.system import (
    is_in_migration_command)

from .constants import ContextParser


class AppConfig(AppConfigBase):  # noqa: D101

    name = __package__

    def _check_rdbms(self):
        """Проверяет, что для модели RouteTemplate используется PostgreSQL.

        PostgreSQL нужна для корректной работы с интервалами.
        """
        if is_in_migration_command():
            return  # pragma: no cover

        db = router.db_for_write(self.get_model('RouteTemplate'))
        engine = settings.DATABASES[db]['ENGINE']
        if engine != 'django.db.backends.postgresql':  # pragma: no cover
            raise ImproperlyConfigured(
                f'Для базы данных "{db}" допустимо использовать только '
                'PostgreSQL.'
            )

    @staticmethod
    def _register_parsers():
        """Регистрирует парсеры параметров контекста."""
        from m3.actions.context import DeclarativeActionContext

        params = (
            (
                ContextParser.INT_TUPLE,
                lambda s: tuple(int(x) for x in s.split(','))
            ),
            (
                ContextParser.INT_OR_NONE,
                lambda x: int(x) if x else None
            ),
        )

        for name, parser in params:
            DeclarativeActionContext.register_parser(name, parser)

    def ready(self):  # noqa: D102
        super().ready()

        self._check_rdbms()
        self._register_parsers()
