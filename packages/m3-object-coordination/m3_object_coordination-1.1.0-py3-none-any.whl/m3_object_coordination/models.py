# coding: utf-8
from builtins import staticmethod
from functools import partial

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.deletion import SET_NULL
from django.db.models.expressions import RawSQL
from django.db.models.signals import class_prepared
from django.db.models.signals import post_delete
from django.dispatch.dispatcher import receiver
from django.utils.timezone import now

import m3_object_coordination

from ._external_utils.db.mixins.date_interval import ActualObjectsManager
from ._external_utils.db.mixins.date_interval import DateIntervalMixin
from ._external_utils.db.mixins.validation import Manager
from ._external_utils.db.mixins.validation import post_clean
from ._external_utils.db.models import BaseModel
from ._external_utils.utils.db import add_intersection_filter
from ._external_utils.utils.db import get_original_field_values
from ._external_utils.utils.validation import IModelValidator
from .constants import REVIEW_RESULT_NAMES
from .constants import ReviewResult


# -----------------------------------------------------------------------------

class PhaseBase(models.Model):

    """Класс-примесь для моделей с полем "Номер" и автонумерацией."""

    # pylint: disable=arguments-differ

    number = models.PositiveSmallIntegerField(
        'Номер этапа в шаблоне',
    )

    class Meta:  # noqa: D106
        abstract = True

    def get_phase_group_identity(self):
        """Возвращает значения, определяющих группу нумеруемых элементов."""
        raise NotImplementedError()  # pragma: no cover

    def clean_fields(self, exclude=None):  # noqa: D102
        group_key = self.get_phase_group_identity()
        if not self.pk and not self.number and all(group_key.values()):
            # Формирование SQL-запроса для определения следующего номера.
            # Такой подход не исключает дублирование номеров при конкурентных
            # запросах, однако снижает вероятность создания этапов с
            # одинаковыми номерами за счет снижения временного интервала между
            # определением следующего номера и созданием этапа.
            def get_db_column(field_name):
                return self._meta.get_field(field_name).get_attname_column()[1]

            conditions = ', '.join(
                f'{get_db_column(field_name)} = %s'
                for field_name in group_key
            )

            self.number = RawSQL(
                (
                    "select coalesce(max({})::integer, 0) + 1 "
                    'from {} '
                    'where {}'
                ).format(
                    self._meta.get_field('number').get_attname_column()[1],
                    self._meta.db_table,
                    conditions,
                ),
                params=tuple(group_key.values()),
            )
            exclude = tuple(exclude or ()) + ('number',)

        super().clean_fields(exclude)

    def validate_unique(self, exclude=None):  # noqa: D102
        if isinstance(self.number, RawSQL):
            exclude = tuple(exclude or ()) + ('number',)

        super().validate_unique(exclude)

    def save(self, *args, **kwargs):  # noqa: D102
        super().save(*args, **kwargs)

        if isinstance(self.number, RawSQL):
            self.refresh_from_db(fields=('number',))

    @staticmethod
    @receiver(post_delete)
    def __renumber(instance, sender, **_):
        """Перенумеровывает объекты после удаления одного из них."""
        if not isinstance(instance, PhaseBase):
            return

        objects = sender.objects.filter(
            **instance.get_phase_group_identity()
        ).order_by('number').iterator()
        for number, obj in enumerate(objects, 1):
            if obj.number != number:
                obj.number = number
                obj.full_clean()
                obj.save(update_fields=('number',))


class ApprooverMixin(models.Model):

    """Класс-примесь с полями, определяющими согласующего на этапе."""

    approover_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        related_name='+',
        verbose_name='Тип согласующего',
    )
    approover_id = models.PositiveIntegerField(
        verbose_name='Id согласующего',
    )
    approover = GenericForeignKey('approover_type', 'approover_id')

    class Meta:  # noqa: D106
        abstract = True

    def _get_object_model(self):
        """Возвращает модель согласуемых объектов."""
        raise NotImplementedError()  # pragma: no cover

    def simple_clean(self, errors):  # noqa: D102
        super().simple_clean(errors)

        if errors:
            return  # pragma: no cover
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка существования объекта согласующего в БД.

        if not self.approover_type.model_class().objects.filter(
            pk=self.approover_id
        ).exists():
            errors['approover_id'].append(
                f'{self.approover_type.model_class()._meta.verbose_name} с '
                f'идентификатором {self.approover_id} не существует.'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка допустимости использования типа объектов.

        object_model = self._get_object_model()
        approover_model = self.approover_type.model_class()
        if not m3_object_coordination.config.can_approove(
            object_model, approover_model
        ):
            errors['approover_type'].append(
                f'Согласование объектов "{object_model._meta.verbose_name}" '
                f'недоступно для "{approover_model._meta.verbose_name}".'
            )

    @staticmethod
    def __auto_delete(model, instance, **_):
        """Удаление согласующих на этапах при удалении связанных объектов.

        :param model: модель согласующего на этапе.
        :param instance: удаляемый согласующий.
        """
        if hasattr(instance, 'id') and isinstance(instance.id, int):
            model.objects.filter(
                approover_type=ContentType.objects.get_for_model(instance),
                approover_id=instance.id,
            ).delete()

    @staticmethod
    @receiver(class_prepared)
    def __set_handlers(sender, **_):
        """Устанавливает обработчики сигналов при создании моделей-потомков."""
        if issubclass(sender, ApprooverMixin):
            post_delete.connect(
                partial(ApprooverMixin.__auto_delete, sender),
                weak=False,
            )


class RootObjectMixin:

    """Класс-примесь для объектов с "корневым" элементом.

    В контексте данного класса-примеси корневыми считаются следующие модели:

      * для RouteTemplateApproover --- RouteTemplate;
      * для RouteApproover --- Route;
      * для Route --- RouteTemplate.
    """

    class Meta:  # noqa: D106
        abstract = True

    class RootObjectMeta:  # noqa: D106

        #: Модель корневого элемента.
        root_model = None

        #: Lookup для доступа к корневому элеенту.
        root_lookup = None

        #: Текст сообщения о недопустимости смены типа объекта.
        error_message = None

    @staticmethod
    def __prevent_object_type_change(model, instance, errors, **_):
        """Предотвращает смену типа объектов.

        Т.к. конфигурация подсистемы предполагает возможность ограничения
        перечня согласующих, изменение типа объекта в шаблоне маршрута может
        нарушить целостность данных. Поэтому там, где определены согласующие,
        смена типа объектов недопустима.

        :param model: модель, зависимая от корневой.
        :param instance: экземпляр корневой модели.
        :param errors: словарь с сообщениями об ошибках в экземпляре корневой
            модели.
        """
        if (
            instance.pk and
            'object_type' not in errors and
            instance.object_type_id != get_original_field_values(
                instance, 'object_type'
            ) and
            model.objects.filter(**{
                model.RootObjectMeta.root_lookup: instance.pk
            }).exists()
        ):
            errors['object_type'].append(model.RootObjectMeta.error_message)

    @staticmethod
    @receiver(class_prepared)
    def __set_handlers(sender, **_):
        """Устанавливает обработчики сигналов при создании моделей-потомков."""
        if (
            issubclass(sender, RootObjectMixin) and
            sender.RootObjectMeta.root_model
        ):
            post_clean.connect(
                partial(RootObjectMixin.__prevent_object_type_change, sender),
                sender.RootObjectMeta.root_model,
                weak=False,
            )
# -----------------------------------------------------------------------------
# Модели для хранения данных шаблонов маршрутов.


class ObjectTypeValidator(IModelValidator):

    """Проверка типа объекта шаблона маршрута согласования."""

    def clean(self, instance, errors):      # :noqa: D102
        object_model = instance.object_type.model_class()
        if not m3_object_coordination.config.can_coordinate(object_model):
            options = getattr(object_model, '_meta')
            errors['object_type'].append(
                f'Для объектов типа "{options.verbose_name}" не '
                'поддерживаются маршруты согласования.'
            )


class RouteTemplateUniqueValidator(IModelValidator):

    """Проверка уникальности шаблона маршрута согласования."""

    @staticmethod
    def _get_unique_params(instance):
        """Возвращает параметры проверки уникальности объекта."""
        return dict(
            object_type=instance.object_type_id,
            default=True,
        )

    def clean(self, instance, errors):      # :noqa: D102
        if (
            instance.default and
            (
                not instance.start_date or
                not instance.end_date or
                instance.start_date <= instance.end_date
            )
        ):
            query = add_intersection_filter(
                RouteTemplate.objects.filter(
                    **self._get_unique_params(instance)
                ),
                *instance.interval_range
            )
            if instance.pk is not None:
                query = query.exclude(pk=instance.pk)
            if query.exists():
                errors['default'].append(
                    'Для этого типа объектов в интервале дат '
                    f'"{instance.interval_range_str}" уже определен шаблон по'
                    ' умолчанию.'
                )


class RouteTemplate(DateIntervalMixin, BaseModel):

    """Модель "Шаблоны маршрута согласования".

    Маршрут согласования состоит из этапов, для каждого из которых назначаются
    подразделения, сотрудники которых выполняют согласование этапа.
    """

    object_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        related_name='+',
        verbose_name='Тип объекта',
    )
    default = models.BooleanField(
        'Шаблон по умолчанию',
        default=False,
    )
    name = models.CharField(
        'Наименование шаблона',
        max_length=255,
    )
    start_date = models.DateField(
        'Дата начала действия',
        blank=True, null=True,
    )
    end_date = models.DateField(
        'Дата окончания действия',
        blank=True, null=True,
    )

    interval_field_names = ('start_date', 'end_date')
    no_intersections_for = ('object_type', 'name')

    objects = Manager()
    actual_objects = ActualObjectsManager()

    validators = [
        RouteTemplateUniqueValidator(),
        ObjectTypeValidator(),
    ]

    class Meta:  # noqa: D106
        verbose_name = 'Шаблон маршрута согласования'
        verbose_name_plural = 'Шаблоны маршрутов согласования'

    def __str__(self):  # noqa: D105
        return f'{self.name} ({self.interval_range_str})'

    def simple_clean(self, errors):  # noqa: D102
        super().simple_clean(errors)

        if errors:
            return  # pragma: no cover


class RouteTemplatePhase(PhaseBase, BaseModel):

    """Модель "Этапы шаблонов маршрута"."""

    template = models.ForeignKey(
        RouteTemplate,
        on_delete=CASCADE,
        related_name='phases',
        verbose_name='Шаблон маршрута',
    )
    name = models.CharField(
        'Наименование этапа',
        max_length=255,
    )
    deadline = models.PositiveSmallIntegerField(
        'Нормативный срок исполнения',
        help_text='Указывается число рабочих дней',
        blank=True, null=True,
    )

    class Meta:  # noqa: D106
        verbose_name = 'Этап шаблона в маршруте'
        verbose_name_plural = 'Этапы шаблона в маршруте'
        unique_together = (
            ('template', 'number'),
        )

    def get_phase_group_identity(self):
        """Возвращает словарь, идентифицирующий группу этапов."""
        return dict(
            template_id=self.template_id,
        )


class RouteTemplateApproover(RootObjectMixin, ApprooverMixin, BaseModel):

    """Модель "Согласующие на этапах шаблона маршрута согласования"."""

    phase = models.ForeignKey(
        RouteTemplatePhase,
        on_delete=CASCADE,
        related_name='approovers',
        verbose_name='Этап маршрута',
    )

    class Meta:  # noqa: D106
        verbose_name = 'Согласующий на этапе маршрута'
        verbose_name_plural = 'Согласующие на этапах маршрутов'
        unique_together = (
            ('phase', 'approover_type', 'approover_id'),
        )

    class RootObjectMeta:  # noqa: D106
        root_model = RouteTemplate
        root_lookup = 'phase__template'
        error_message = (
            'Смена типа объекта недопустима, т.к. в этапах согласования '
            'шаблона маршрута определены согласующие.'
        )

    def _get_object_model(self):
        """Возвращает модель согласуемых объектов."""
        return self.phase.template.object_type.model_class()
# -----------------------------------------------------------------------------
# Модели для хранения данных маршрутов.


class Route(RootObjectMixin, BaseModel):

    """Модель "Маршрут объекта".

    Маршрут согласования состоит из этапов, для каждого из которых назначаются
    подразделения, сотрудники которых выполняют согласование этапа.
    """

    object_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        related_name='+',
        verbose_name='Тип объекта',
    )
    object_id = models.PositiveIntegerField(
        verbose_name='Id объекта',
    )
    object = GenericForeignKey('object_type', 'object_id')

    template = models.ForeignKey(
        RouteTemplate,
        on_delete=SET_NULL,
        related_name='routes',
        verbose_name='Шаблон маршрута',
        # Непустое значение указывает на то, что маршрут создан из шаблона.
        blank=True, null=True,
    )

    class Meta:  # noqa: D106
        verbose_name = 'Маршрут объекта'
        verbose_name_plural = 'Маршруты объектов'
        unique_together = (
            ('object_type', 'object_id'),
        )

    class RootObjectMeta:  # noqa: D106
        root_model = RouteTemplate
        root_lookup = 'template'
        error_message = (
            'Смена типа объекта недопустима, т.к. для на основе данного .'
            'шаблона уже созданы маршруты.'
        )

    def simple_clean(self, errors):  # noqa: D102
        super().simple_clean(errors)

        if errors:
            return  # pragma: no cover
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка существования объекта согласования в БД.

        if not self.object_type.model_class().objects.filter(
            pk=self.object_id
        ).exists():
            errors['object_id'].append(
                f'{self.object_type.model_class()._meta.verbose_name} с '
                f'идентификатором {self.object_id} не существует.'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        object_model = self.object_type.model_class()
        if not m3_object_coordination.config.can_coordinate(object_model):
            options = getattr(object_model, '_meta')
            errors['object_type'].append(
                f'Для объектов типа "{options.verbose_name}" не '
                'поддерживаются маршруты согласования.'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка соответствия типа объектов в маршруте и в шаблоне маршрута.
        # Обратная проверка реализована в __on_route_template_change.

        if (
            self.template_id and
            self.template.object_type_id != self.object_type_id
        ):
            errors['object_type'].append(
                'Типы объекта в маршруте и шаблоне не совпадают.'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    @receiver(post_delete)
    def __auto_delete(instance, **_):
        """Удаляет маршрут при удалении объектов."""
        if hasattr(instance, 'id') and isinstance(instance.id, int):
            Route.objects.filter(
                object_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id,
            ).delete()


class RoutePhase(PhaseBase, BaseModel):

    """Модель "Этап маршрута объекта"."""

    route = models.ForeignKey(
        Route,
        on_delete=CASCADE,
        related_name='phases',
        verbose_name='Маршрут',
    )
    name = models.CharField(
        'Наименование этапа',
        max_length=255,
    )
    deadline = models.PositiveSmallIntegerField(
        'Нормативный срок исполнения',
        help_text='Указывается число рабочих дней',
        blank=True, null=True,
    )
    planned_date = models.DateField(
        'Плановая дата исполнения',
        # Заполняется только после завершения предыдущего этапа.
        blank=True, null=True,
    )
    actual_date = models.DateField(
        'Фактическая дата исполнения',
        # Заполняется только после завершения текущего этапа.
        blank=True, null=True,
    )
    template = models.ForeignKey(
        RouteTemplatePhase,
        on_delete=SET_NULL,
        related_name='+',
        verbose_name='Шаблон этапа',
        # Непустое значение указывает на то, что этап создан из шаблона.
        blank=True, null=True,
    )

    class Meta:  # noqa: D106
        verbose_name = 'Этап маршрута объекта'
        verbose_name_plural = 'Этапы маршрутов объектов'
        unique_together = (
            ('route', 'number'),
        )

    def get_phase_group_identity(self):
        """Возвращает словарь, идентифицирующий группу этапов."""
        return dict(
            route_id=self.route_id,
        )

    def is_first(self) -> bool:
        """Возвращает True, если этап является первым в маршруте."""
        return not RoutePhase.objects.filter(
            route_id=self.route_id,
            number__lt=self.number,
        ).exists()

    def is_last(self) -> bool:
        """Возвращает True, если этап является последним в маршруте."""
        return not RoutePhase.objects.filter(
            route_id=self.route_id,
            number__gt=self.number,
        ).exists()


class RouteApproover(RootObjectMixin, ApprooverMixin, BaseModel):

    """Модель "Согласующий на этапе маршрута"."""

    phase = models.ForeignKey(
        RoutePhase,
        on_delete=CASCADE,
        related_name='approovers',
        verbose_name='Этап маршрута',
    )

    approover_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        related_name='+',
        verbose_name='Тип согласующего',
    )
    approover_id = models.PositiveIntegerField(
        verbose_name='Id согласующего',
    )
    approover = GenericForeignKey('approover_type', 'approover_id')

    template = models.ForeignKey(
        RouteTemplateApproover,
        on_delete=SET_NULL,
        related_name='+',
        verbose_name='Согласующий на этапе шаблона маршрута',
        # Непустое значение указывает на то, что этап создан из шаблона.
        blank=True, null=True,
    )

    class Meta:  # noqa: D106
        verbose_name = 'Согласующий на этапе маршрута объекта'
        verbose_name_plural = 'Согласующие на этапе маршрута объекта'
        unique_together = (
            ('phase', 'approover_type', 'approover_id'),
        )

    class RootObjectMeta:  # noqa: D106
        root_model = Route
        root_lookup = 'phase_route'
        error_message = (
            'Смена типа объекта недопустима, т.к. в этапах согласования '
            'маршрута определены согласующие.'
        )

    def _get_object_model(self):
        """Возвращает модель согласуемых объектов."""
        return self.phase.route.object_type.model_class()
# -----------------------------------------------------------------------------


class Log(BaseModel):

    """Модель "Журнал согласования"."""

    approover = models.ForeignKey(
        RouteApproover,
        on_delete=CASCADE,
        related_name='log_records',
        verbose_name='Согласующий',
    )

    # Пользователь, проставивший отметку о согласовании.
    user_type = models.ForeignKey(
        ContentType,
        on_delete=CASCADE,
        related_name='+',
        # Пустое значение указывает на то, что изменение сделано Системой.
        blank=True, null=True,
    )
    user_id = models.PositiveIntegerField(
        # Пустое значение указывает на то, что изменение сделано Системой.
        blank=True, null=True,
    )
    user = GenericForeignKey('user_type', 'user_id')

    result = models.PositiveSmallIntegerField(
        'Результат согласования',
        choices=tuple(REVIEW_RESULT_NAMES.items())
    )
    timestamp = models.DateTimeField(
        'Дата и время согласования',
        default=now,
    )
    comment = models.TextField(
        'Комментарий',
        blank=True, null=True,
    )
    actual = models.BooleanField(
        'Актуальность записи',
        # False указывает на то, что запись является исторической.
        default=True,
    )

    class Meta:  # noqa: D106
        verbose_name = 'Запись журнала согласования'
        verbose_name_plural = 'Журнал согласования'

    def simple_clean(self, errors):  # noqa: D102
        super().simple_clean(errors)

        if errors:
            return  # pragma: no cover
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка наличия комментария при отрицательном результате
        # согласования.

        if self.result != ReviewResult.AGREED and not self.comment:
            errors['comment'].append(
                'В случае отказа или отправки на доработку нужно указать '
                'причину.'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка существования объекта согласующего в БД.

        if (
            self.user_type_id and
            self.user_id and
            not self.user_type.model_class().objects.filter(
                pk=self.user_id
            ).exists()
        ):
            errors['user_id'].append(
                f'{self.user_type.model_class()._meta.verbose_name} с '
                f'идентификатором {self.user_id} не существует.'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    @receiver(post_delete)
    def __auto_delete(instance, **_):
        """Удаляет записи из журнала при удалении пользователя."""
        if hasattr(instance, 'id') and isinstance(instance.id, int):
            Log.objects.filter(
                user_type=ContentType.objects.get_for_model(instance),
                user_id=instance.id,
            ).delete()
# -----------------------------------------------------------------------------
