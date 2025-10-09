# coding: utf-8
from collections import defaultdict
from functools import wraps
import inspect
import sys

from django.core.exceptions import NON_FIELD_ERRORS
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models.base import Model
from django.db.models.base import ModelBase
from django.db.transaction import atomic
from django.utils.encoding import force_text
from m3.actions import Action
from m3.actions import ActionPack
from m3.actions import ControllerCache
from objectpack.exceptions import ValidationError as ObjectPackValidationError
from objectpack.models import ModelProxy
from objectpack.models import ModelProxyMeta
from objectpack.observer.base import ObservableController
import six


def convert_validation_error_to(exc, new_line='<br/>', model=None):
    """Декоратор, преобразующий исключение
    django.core.exceptions.ValidationError, генерируемое в декорируемой
    функции, в исключение, указанное в аргументе exc путем объединения всех
    сообщений об ошибках из ValidationError.message_dict в одно сообщение, по
    одной ошибке на строку.

    Пример использования:

        class Pack(ObjectPack):
            ...
            @convert_validation_error_to(ApplicationLogicException)
            def save_row(self, obj, create_new, request, context):
                obj.full_clean()
                ...

    :param exc: класс исключения, к которому будет преобразовываться
        ValidationError
    :type exc: subclass of Exception

    :param unicode new_line: разделитель строк в сообщении об ошибке

    :param model: Модель, в которой осуществляется валидация. Должна
        использоваться в тех случаях, когда исключение ValidationError
        генерируется вне модели (например, в методе ObjectPack.save_row).
        Если аргумент указан, то данные будут извлекаться именно из этой
        модели.
    """
    def get_model_meta(error):
        if model is not None:
            return model._meta

        # Достанем из стека вызовов объект модели, в которой было
        # вызвано исключение. Из него будем брать verbose_name полей.
        tb = sys.exc_info()[-1]  # traceback
        # Фрейм, в котором сгенерировано исключение, будет последним.
        error_frame = inspect.getinnerframes(tb)[-1][0]
        # f_locals - локальные переменные функции, в т.ч. аргументы.
        if 'self' not in error_frame.f_locals:
            raise
        model_instance = error_frame.f_locals['self']
        return model_instance._meta

    def get_messages_from_dict(model_meta, data):
        result = []
        for field_name, field_errors in six.iteritems(data):
            if field_name == NON_FIELD_ERRORS:
                result.append(
                    new_line.join(
                        '- {0}'.format(err) for err in field_errors
                    )
                )
            else:
                model_field = model_meta.get_field(field_name)
                verbose_name = (model_field.verbose_name or '')
                result.append(new_line.join(
                    '- {0}: {1}'.format(verbose_name, err)
                    for err in field_errors
                ))
        return result

    def get_messages_from_list(messages):
        result = [
            '- ' + message
            for message in messages
        ]
        return result

    assert issubclass(exc, Exception), type(exc)
    new_line = six.text_type(new_line)

    def decorator(func):
        assert inspect.ismethod(func) or inspect.isfunction(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except DjangoValidationError as e:
                model_meta = get_model_meta(e)

                if hasattr(e, 'message_dict'):
                    title = 'На форме имеются некорректно заполненные поля:'
                    messages = [title] + get_messages_from_dict(model_meta,
                                                                e.message_dict)
                else:
                    title = 'При проверке данных найдены ошибки:'
                    messages = [title] + get_messages_from_list(e.messages)
                messages.insert(1, '')

                raise exc(new_line.join(messages))

        return wrapper

    return decorator


class PackValidationMixin:

    """Примесь к пакам из objectpack, добавляющая валидацию моделей.

    Перед сохранением объекта в методе *save_row()* пака выполняется проверка
    данных путем вызова метода *full_clean()* сохраняемого объекта.

    .. note::
       При использовании в паке составной модели
       (*objectpack.models.ModelProxy*) в такой модели должен быть реализован
       метод *full_clean()* (см. *ModelProxyValidationMixin* и
       *BaseModelProxy*).

    Пример использования:

       class UnitPack(PackValidationMixin, TreeObjectPack):
           ...

       class PeriodPack(PackValidationMxin, ObjectPack):
           ....
    """

    @convert_validation_error_to(ObjectPackValidationError)
    def save_row(self, obj, create_new, request, context):
        """Вызывает проверку данных перед их сохранением в БД."""
        from objectpack.slave_object_pack.actions import SlavePack
        if isinstance(self, SlavePack):
            obj.__dict__.update(
                self._get_parents_dict(context, key_fmt='%s_id')
            )
            save_row = super(SlavePack, self).save_row
        else:
            save_row = super(PackValidationMixin, self).save_row

        if getattr(obj, 'clean_and_save_inside_transaction', False):
            with atomic():
                obj.full_clean()
                save_row(obj, create_new, request, context)
        else:
            obj.full_clean()
            save_row(obj, create_new, request, context)
