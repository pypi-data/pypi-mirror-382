# coding: utf-8


class SingletonMeta(type):

    """Метакласс для классов-одиночек.

    Потомки класса с данным метаклассом также будут одиночками. Инициализация
    классов-одиночек (вызов метода ``__init__``) будет выполняться один раз
    при создании.

    .. code-block:: python

       class SingleClass(object):
           __metaclass__ = SingletonMeta
    """

    def __init__(cls, name, bases, attrs):  # noqa: D107
        super(SingletonMeta, cls).__init__(name, bases, attrs)
        cls.instance = None

    def __call__(cls, *args, **kwargs):  # noqa: D102
        if cls.instance is None:
            cls.instance = super(SingletonMeta, cls).__call__(*args, **kwargs)

        return cls.instance
