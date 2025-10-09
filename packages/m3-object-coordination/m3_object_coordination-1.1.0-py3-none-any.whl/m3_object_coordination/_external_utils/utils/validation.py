# coding: utf-8
from abc import ABCMeta
from abc import abstractmethod

from six import with_metaclass


class IModelValidator(with_metaclass(ABCMeta, object)):
    """Базовый класс валидатора модели."""

    @abstractmethod
    def clean(self, instance, errors):
        """Валидирует объект.

        :param instance: экземпляр проверяемой модели.
        :type instance: django.db.models.base.Model

        :param errors: ошибки, выявленные в ходе проверки.
        :type errors: collections.OrderedDict
        """
        raise NotImplementedError()
