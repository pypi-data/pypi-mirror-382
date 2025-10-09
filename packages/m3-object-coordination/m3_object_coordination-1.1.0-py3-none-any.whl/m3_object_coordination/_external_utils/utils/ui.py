# coding: utf-8
from os.path import abspath
from os.path import dirname
from os.path import join
import inspect

from django.conf import settings


def local_template(file_name):
    """Возвращает абсолютный путь к файлу относительно модуля.

    Основное предназначение -- формирование значений полей ``template`` и
    ``template_globals`` окон, вкладок и других компонент пользовательского
    интерфейса в тех случаях, когда файл шаблона размещен в той же папке, что
    и модуль с компонентом.

    :param str file_name: Имя файла.

    :rtype: str
    """
    frame = inspect.currentframe().f_back

    root_package_name = frame.f_globals['__name__'].rsplit('.', 2)[0]
    module = __import__(root_package_name)

    TEMPLATE_DIRS = set(
        path
        for config in settings.TEMPLATES
        for path in config.get('DIRS', ())
    )

    assert any(
        dirname(path) in TEMPLATE_DIRS
        for path in module.__path__
    ), (
        f'Пакет "{module.__path__}" должен быть указан в параметре TEMPLATES '
        'проекта.',
        TEMPLATE_DIRS,
    )

    # Путь к модулю вызывающей функции
    module_path = abspath(dirname(frame.f_globals['__file__']))

    for path in TEMPLATE_DIRS:
        if module_path.startswith(path):
            module_path = module_path[len(path) + 1:]
            break

    return join(module_path, file_name)
