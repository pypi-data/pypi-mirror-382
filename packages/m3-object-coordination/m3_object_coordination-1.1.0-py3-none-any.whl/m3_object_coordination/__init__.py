# coding: utf-8
# pylint: disable=unsupported-membership-test,unsubscriptable-object
from abc import ABCMeta
from abc import abstractmethod
from datetime import date
from inspect import isclass
from typing import Optional
from typing import Set
from typing import Type
from typing import Union

from django.apps import apps as django_apps
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import request_started
from django.db.backends.signals import connection_created
from django.db.models.base import Model
from django.db.models.base import ModelBase
from django.http.request import HttpRequest


default_app_config = __name__ + '.apps.AppConfig'


def get_model_name(
    model: Union[int, str, Model, ModelBase]
) -> Optional[ModelBase]:
    """Возвращает имя модели в формате ``app_label.ModelName``.

    Модель может быть задана целочисленным идентификатором типа
    (``ContentType.id``), строкой с именем django-приложения и именем модели
    (``'app_label.ModelName'``), объектом модели или классом самой модели.
    """
    assert isinstance(model, (int, str, Model, ModelBase)), type(model)

    if isinstance(model, int):
        ContentType = django_apps.get_model('contenttypes', 'ContentType')
        try:
            model = ContentType.objects.get_for_id(model).model_class()
        except ContentType.DoesNotExist:
            model = None

    elif isinstance(model, str):
        names = model.split('.')
        if len(names) == 2:
            try:
                model = django_apps.get_model(*names)
            except LookupError:
                model = None
        else:
            model = None

    elif isinstance(model, Model):
        model = model.__class__

    if model is None:
        result = None
    else:
        result = f'{model._meta.app_label}.{model._meta.object_name}'

    return result


class IConfig(metaclass=ABCMeta):

    """Интерфейс класса конфигурации подсистемы согласования."""

    @abstractmethod
    def can_coordinate(
        self,
        obj: Union[int, str, Model, ModelBase],
    ) -> bool:
        """Возвращает True, если разрешено согласование указанного объекта.

        :param obj: согласуемый объект, либо модель.
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def can_approove(
        self,
        route_object: Union[int, str, Model, ModelBase],
        approover_object: Union[int, str, Model, ModelBase],
    ) -> bool:
        """Возвращает True, если согласование объекта допустимо.

        Например, с помощью этого метода можно разрешить согласование заявок
        только подразделениям организации, т.е. в маршрутах согласования
        заявок будет разрешено указывать только подразделения.

        :param route_object: согласуемый объект (например, заявка).
        :param approover_object: согласующий объект (например, подразделение
            организации).
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def can_approove_as(
        self,
        user: Model,
        approover_object: Model
    ) -> bool:
        """Возвращает True, если разрешено согласование от имени согласующего.

        Например, если согласующим в этапе согласования указано какое-либо
        подразделение, то согласование может быть разрешено сотрудникам этого
        подразделения.

        :param user: пользователь, рассматривающий объект согласования.
        :param approover: согласующий.
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def is_working_day(
        self,
        day: date,
    ) -> bool:
        """Возвращает True, если указанный день является рабочим.

        :param day: дата, на которую определяется режим работы.
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_current_user(
        self,
        request: HttpRequest,
    ) -> Model:
        """Возвращает пользователя, рассматривающего объект согласования.

        :param request: HTTP-запрос.
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_approover_select_pack_for(
        self,
        approover_model: Union[int, str, Model, ModelBase],
    ):
        """Возвращает пак для выбора объектов указанного типа.

        :param approover_model: тип объектов согласующих.

        :rtype: m3.actions.ActionPack
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_object_repr(self, obj) -> str:
        """Возвращает текстовое представление согласуемого объекта.

        :param obj: согласуемый объект.
        :type obj: django.db.models.base.Model

        :rtype: str
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_approover_repr(self, approover) -> str:
        """Возвращает текстовое представление объекта согласующего.

        :param approover: объект согласующего.
        :type approover: django.db.models.base.Model

        :rtype: str
        """
        raise NotImplementedError()  # pragma: no cover

    @abstractmethod
    def get_user_repr(self, user) -> str:
        """Возвращает текстовое представление пользователя.

        :param user: пользователь, проставивший отметку о согласовании.
        :type user: django.db.models.base.Model

        :rtype: str
        """
        raise NotImplementedError()  # pragma: no cover


class Config(IConfig):

    """Конфигурация пакета m3-object-coordination."""

    #: Согласуемые модели и их согласующие.
    #:
    #: Ключами словаря являются имена тех моделей, объекты которых могут
    #: использоваться в качестве объектов согласования. Значениями ключей
    #: могут быть значения ``None``, либо коллекция имён моделей, объекты
    #: которых могут быть согласующими для указанной в ключе словаря модели.
    #:
    #: Например, если в проекте модель учетной записи называется
    #: ``'user.User'``, то для того, чтобы разрешить согласование заявок
    #: (модель ``'request.Request'``), нужно указать в параметре ``models``
    #: следующее:
    #:
    #: .. code-block:: python
    #:
    #:    config.models = {
    #:        'request.Request': (
    #:            'user.User',
    #:        ),
    #:    }
    #:
    #: Ключ ``None`` определяет согласующих по умолчанию. Значение ключа
    #: ``None`` указывает на то, что согласующими могут быть любые модели
    #: Системы. Значение ``None`` параметра ``models`` аналогично
    #: ``{None: None}``.
    #:
    #: .. important::
    #:
    #:    При изменении конфигурации помните о том, что уже имеющиеся в БД
    #:    маршруты и шаблоны маршрутов могут утратить актуальность.
    models = None

    def __validate(self, **_):
        """Выполняет проверку корректности параметров."""
        for attr in (
            'models',
            'select_packs_by_approover_type',
            'approover_representers',
            'user_representers',
        ):
            value = getattr(self, attr)
            if value is None:
                continue  # pragma: no cover

            for full_model_name in value:  # pylint: disable=not-an-iterable
                if full_model_name is None:
                    continue  # pragma: no cover

                app_label, model_name = full_model_name.split('.')
                if (
                    app_label not in django_apps.all_models or
                    model_name.lower() not in django_apps.all_models[app_label]
                ):
                    raise ImproperlyConfigured(
                        f'В m3_object_coordination.config.{attr} определена '
                        f'несуществующая модель: {full_model_name}.'
                    )  # pragma: no cover

        connection_created.disconnect(self.__validate)

    def __init__(self):  # noqa: D107
        connection_created.connect(self.__validate)

    def can_coordinate(
        self,
        obj: Union[int, str, Model, ModelBase],
    ):
        """Возвращает True, если разрешено согласование указанного объекта.

        .. seealso::

           :attr:`~m3_object_coordination.Config.models`

        :param obj: согласуемый объект, либо модель.
        """
        assert isinstance(obj, (int, str, Model, ModelBase)) and obj, type(obj)

        model_name = get_model_name(obj)

        return (
            not self.models or
            model_name in self.models or
            None in self.models
        )

    def can_approove(
        self,
        route_object: Union[int, str, Model, ModelBase],
        approover_object: Union[int, str, Model, ModelBase],
    ) -> bool:
        """Возвращает True, если согласование объекта допустимо.

        Например, с помощью этого метода можно разрешить согласование заявок
        только подразделениям организации, т.е. в маршрутах согласования
        заявок будет разрешено указывать только подразделения.

        .. seealso::

           :attr:`~m3_object_coordination.Config.models`

        :param route_object: согласуемый объект (например, заявка).
        :param approover_object: согласующий объект (например, отдел
            организации).
        """
        assert (
            isinstance(route_object, (int, str, Model, ModelBase)) and
            route_object
        ), type(route_object)
        assert (
            isinstance(approover_object, (int, str, Model, ModelBase)) and
            approover_object
        ), type(approover_object)

        route_object_model_name = get_model_name(route_object)
        approover_object_model_name = get_model_name(approover_object)

        if self.models is None:
            result = True
        elif route_object_model_name in self.models:
            route_object_model = self.models[route_object_model_name]
            result = (
                route_object_model is None or
                approover_object_model_name == route_object_model or
                approover_object_model_name in route_object_model
            )
        elif None in self.models:
            default_model = self.models[None]
            result = (
                default_model is None or
                approover_object_model_name == default_model or
                approover_object_model_name in default_model
            )
        else:
            result = False  # pragma: no cover

        return result

    def can_approove_as(
        self,
        user: Model,
        approover_object: Model
    ) -> bool:
        """Возвращает True, если разрешено согласование от имени согласующего.

        Например, если согласующим в этапе согласования указано какое-либо
        подразделение, то согласование может быть разрешено сотрудникам этого
        подразделения.

        Согласование разрешается, если пользователь и согласующий совпадают.

        .. note::

           В исходной реализации согласование разрешается, если пользователь и
           согласующий совпадают. При необходимости переопределяется из
           проекта, использующего подсистему согласования.

        :param user: пользователь, рассматривающий объект согласования.
        :param approover_object: согласующий.
        """
        return user == approover_object  # pragma: no cover

    @staticmethod
    def is_working_day(
        day: date,
    ) -> bool:
        """Возвращает True, если указанный день является рабочим.

        .. note::

           В исходной реализации все дни, кроме субботы и воскресенья, считает
           рабочими. При необходимости переопределяется из проекта,
           использующего подсистему согласования.

        .. warning::

           При реализации функции в проекте следует учитывать реализацию
           функции :func:`m3_object_coordination.utils.add_working_days`, в
           которой вызов данного метода происходит для **каждой** даты в
           интервале между исходной датой и результирующей. В связи с этим
           рекомендуется уделить должное внимание оптимизации.

        :param day: дата, на которую определяется режим работы.
        """
        return day.weekday() < 5

    def get_current_user(
        self,
        request: HttpRequest,
    ) -> Model:
        """Возвращает пользователя, рассматривающего объект согласования.

        Таким пользователем считается текущий пользователь Django.

        :param request: HTTP-запрос.
        """
        return request.user  # pragma: no cover

    #: Паки для выбора согласующих с разбивкой по модели согласующего.
    #:
    #: .. code-block:: python
    #:
    #:    select_packs_by_approover_type = {
    #:        'app1.User1': pack_instance,
    #:    }
    select_packs_by_approover_type = {}

    def get_approover_select_pack_for(
        self,
        approover_model: Union[int, str, Model, ModelBase],
    ):
        """Возвращает пак для выбора объектов указанного типа.

        :rtype: m3.actions.ActionPack
        """
        model_name = get_model_name(approover_model)
        result = self.select_packs_by_approover_type[model_name]
        return result

    #: Преобразователи объектов согласования к строковому представлению.
    #:
    #: В качестве преобразователя по умолчанию используется :func:`str`.
    #: Изменить преобразователь по умолчанию можно через ключ ``None``.
    #:
    #: .. code-block::
    #:
    #:    object_representers = {
    #:        'app1.User1': repr,
    #:    }
    object_representers = {}

    def get_object_repr(self, obj: Model) -> str:
        """Возвращает текстовое представление согласуемого объекта.

        :param obj: согласуемый объект.

        :rtype: str
        """
        model_name = get_model_name(obj)
        default = self.object_representers.get(None, str)
        representer = self.object_representers.get(model_name, default)

        return representer(obj)

    #: Преобразователи объектов согласующих к строковому представлению.
    #:
    #: В качестве преобразователя по умолчанию используется :func:`str`.
    #: Изменить преобразователь по умолчанию можно через ключ ``None``.
    #:
    #: .. code-block::
    #:
    #:    approover_representers = {
    #:        'app1.User1': repr,
    #:    }
    approover_representers = {}

    def get_approover_repr(self, approover: Model) -> str:
        """Возвращает текстовое представление объекта согласующего.

        :param approover: объект согласующего.

        :rtype: str
        """
        model_name = get_model_name(approover)
        default = self.approover_representers.get(None, str)
        representer = self.approover_representers.get(model_name, default)

        return representer(approover)

    #: Преобразователи объектов пользователей к строковому представлению.
    #:
    #: В качестве преобразователя по умолчанию используется :func:`str`.
    #: Изменить преобразователь по умолчанию можно через ключ ``None``.
    #:
    #: .. code-block::
    #:
    #:    approover_representers = {
    #:        'app1.User1': repr,
    #:    }
    user_representers = {}

    def get_user_repr(self, user: Optional[Model]) -> str:
        """Возвращает текстовое представление пользователя.

        :param user: пользователь, проставивший отметку о согласовании.

        :rtype: str
        """
        if user is None:
            result = ''
        else:
            model_name = get_model_name(user)
            default = self.user_representers.get(None, str)
            representer = self.user_representers.get(model_name, default)
            result = representer(user)

        return result


#: Конфигурация пакета.
#:
#: При необходимости изменения настроек по умолчанию данный атрибут модуля
#: перезаписывается экземпляром другого класса конфигурации, либо значения
#: параметров изменяются прямо в данном объекте.
config = Config()
