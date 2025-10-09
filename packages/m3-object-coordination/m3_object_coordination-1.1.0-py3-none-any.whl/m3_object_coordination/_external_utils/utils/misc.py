# coding: utf-8
from pathlib import Path
import inspect

from ..._external_utils import Undefined


class cached_property(property):

    """Кешируемое свойство.

    В отличие от :class:`django.utils.functional.cached_property`, наследуется
    от property и копирует строку документации, что актуально при генерации
    документации средствами Sphinx.
    """

    def __init__(self, method):  # noqa: D107
        super(cached_property, self).__init__(method)

        self.__doc__ = method.__doc__

    def __get__(self, instance, owner):  # noqa: D105
        if instance is None:
            return self

        if self.fget.__name__ not in instance.__dict__:
            instance.__dict__[self.fget.__name__] = self.fget(instance)

        return instance.__dict__[self.fget.__name__]


class NoOperationCM:

    """Менеджер контекта, не выполняющий никаких действий."""

    def __enter__(self):  # noqa: D105
        return self

    def __exit__(self, ex_type, ex_inst, traceback):  # noqa: D105
        pass


def get_local_path(file_name):
    u"""Возвращает абсолютный путь к файлу относительно модуля.

    :param str file_name: Имя файла.

    :rtype: str
    """
    frame = inspect.currentframe().f_back
    return Path(frame.f_globals['__file__']).absolute().parent.joinpath(
        file_name
    )


def is_ranges_intersected(range1, range2):
    u"""Возвращает True, если указанные интервалы значений пересекаются.

    Интервалы задаются в виде двухэлементных кортежей, первый элемент кортежа
    определяет начало интервала, а второй - конец интервала. None определяет
    открытый с соответствующей стороны интервал.

    Типы данных в интервалах должны поддерживать сравнение значений с помощью
    оператора <=.

    :rtype: bool
    """
    (from1, to1), (from2, to2) = range1, range2

    assert from1 is None or to1 is None or from1 <= to1, (from1, to1)
    assert from2 is None or to2 is None or from2 <= to2, (from2, to2)

    if from1 is None and to1 is None:
        result = True

    elif from1 is not None and to1 is None:
        result = to2 is None or from1 <= to2

    elif from1 is None and to1 is not None:
        result = from2 is None or from2 <= to1

    else:  # from1 is not None and to1 is not None
        if from2 is None and to2 is None:
            result = True

        elif from2 is not None and to2 is None:
            result = from2 <= to1

        elif from2 is None and to2 is not None:
            result = from1 <= to2

        else:  # from2 is not None and to2 is not None
            result = from2 <= to1 and from1 <= to2

    return result


def get_nested_attr(obj, attr, default=Undefined):
    u"""Возвращает значение вложенного атрибута объекта.

    .. code-block:: python

       obj = datetime(2015, 1, 1, 0, 0, 0)
       get_nested_attr(obj, 'date().year')  # 2015
       get_nested_attr(obj, 'date().year.__class__')  # int
    """
    attributes = attr.split('.')

    nested_attribute = ''
    nested_object = obj
    for name in attributes:
        if nested_attribute:
            nested_attribute += '.'
        nested_attribute += name

        if name.endswith('()'):
            callable_attribute = True
            name = name[:-2]
        else:
            callable_attribute = False

        try:
            nested_object = getattr(nested_object, name)
            if callable_attribute:
                assert callable(nested_object), (name, nested_object)
                nested_object = nested_object()
        except AttributeError:
            if default is not Undefined:
                return default
            else:
                raise AttributeError(
                    "'{}' object has no attribute '{}'".format(
                        type(obj), nested_attribute
                    )
                )

    return nested_object
