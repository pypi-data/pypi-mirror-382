# coding: utf-8
from inspect import currentframe


def is_in_migration_command():
    u"""Возвращает True, если код выполняется в рамках миграций South/Django.

    :rtype: bool
    """
    commands = ('migrate', 'makemigrations', 'sqlmigrate', 'showmigrations')

    frame = currentframe()
    while frame:
        if 'self' in frame.f_locals:
            self_class = frame.f_locals['self'].__class__
            if (
                self_class.__name__ == 'Command' and
                self_class.__module__ in (
                    'django.core.management.commands.' + command
                    for command in commands
                )
            ):
                return True

            elif (
                self_class.__name__ == 'ManagementUtility' and
                self_class.__module__ == 'django.core.management'
            ):
                # Срабатывает при использовании функции в AppConfig
                if 'subcommand' in frame.f_locals:
                    subcommand = frame.f_locals['subcommand']
                    return subcommand in commands

        frame = frame.f_back

    return False
