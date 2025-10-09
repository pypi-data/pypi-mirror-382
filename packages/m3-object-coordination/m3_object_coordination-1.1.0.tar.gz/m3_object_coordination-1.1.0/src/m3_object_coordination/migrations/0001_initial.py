# coding: utf-8
from django.db import migrations
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.deletion import SET_NULL
from django.utils.timezone import now

from m3_object_coordination.models import RootObjectMixin

from ..constants import ReviewResult


class Migration(migrations.Migration):  # noqa: D101

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('user_id', models.PositiveIntegerField(blank=True,
                                                        null=True)),
                ('result',
                 models.PositiveSmallIntegerField(
                     choices=[
                         (ReviewResult.AGREED, 'Согласовано'),
                         (ReviewResult.NEED_CHANGES, 'На доработку'),
                         (ReviewResult.REJECTED, 'Отклонено'),
                     ],
                     verbose_name='Результат согласования')),
                ('timestamp',
                 models.DateTimeField(
                     default=now,
                     verbose_name='Дата и время согласования')),
                ('comment',
                 models.TextField(
                     blank=True, null=True, verbose_name='Комментарий')),
                ('actual',
                 models.BooleanField(
                     verbose_name='Актуальность записи', default=True)),
            ],
            options={
                'verbose_name': 'Запись журнала согласования',
                'verbose_name_plural': 'Журнал согласования',
            },
        ),
        migrations.CreateModel(
            name='Route',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('object_id',
                 models.PositiveIntegerField(verbose_name='Id объекта')),
                ('object_type',
                 models.ForeignKey(
                     on_delete=CASCADE,
                     related_name='+',
                     to='contenttypes.ContentType',
                     verbose_name='Тип объекта')),
            ],
            options={
                'verbose_name': 'Маршрут объекта',
                'verbose_name_plural': 'Маршруты объектов',
            },
            bases=(RootObjectMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RouteApproover',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('approover_id',
                 models.PositiveIntegerField(verbose_name='Id согласующего')),
                ('approover_type',
                 models.ForeignKey(
                     on_delete=CASCADE,
                     related_name='+',
                     to='contenttypes.ContentType',
                     verbose_name='Тип согласующего')),
            ],
            options={
                'verbose_name': 'Согласующий на этапе маршрута объекта',
                'verbose_name_plural': 'Согласующие на этапе маршрута объекта',
            },
            bases=(RootObjectMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RoutePhase',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('number',
                 models.PositiveSmallIntegerField(
                     verbose_name='Номер этапа в шаблоне')),
                ('name',
                 models.CharField(
                     max_length=255, verbose_name='Наименование этапа')),
                ('deadline',
                 models.PositiveSmallIntegerField(
                     blank=True,
                     help_text='Указывается число рабочих дней',
                     null=True,
                     verbose_name='Нормативный срок исполнения')),
                ('planned_date',
                 models.DateField(
                     blank=True,
                     null=True,
                     verbose_name='Плановая дата исполнения')),
                ('actual_date',
                 models.DateField(
                     blank=True,
                     null=True,
                     verbose_name='Фактическая дата исполнения')),
                ('route',
                 models.ForeignKey(
                     on_delete=CASCADE,
                     related_name='phases',
                     to='m3_object_coordination.Route',
                     verbose_name='Маршрут')),
            ],
            options={
                'verbose_name': 'Этап маршрута объекта',
                'verbose_name_plural': 'Этапы маршрутов объектов',
            },
        ),
        migrations.CreateModel(
            name='RouteTemplate',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('default',
                 models.BooleanField(
                     default=False, verbose_name='Шаблон по умолчанию')),
                ('name',
                 models.CharField(
                     max_length=255, verbose_name='Наименование шаблона')),
                ('start_date',
                 models.DateField(
                     blank=True,
                     null=True,
                     verbose_name='Дата начала действия')),
                ('end_date',
                 models.DateField(
                     blank=True,
                     null=True,
                     verbose_name='Дата окончания действия')),
                ('object_type',
                 models.ForeignKey(
                     on_delete=CASCADE,
                     related_name='+',
                     to='contenttypes.ContentType',
                     verbose_name='Тип объекта')),
            ],
            options={
                'verbose_name': 'Шаблон маршрута согласования',
                'verbose_name_plural': 'Шаблоны маршрутов согласования',
            },
        ),
        migrations.CreateModel(
            name='RouteTemplateApproover',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('approover_id',
                 models.PositiveIntegerField(verbose_name='Id согласующего')),
                ('approover_type',
                 models.ForeignKey(
                     on_delete=CASCADE,
                     related_name='+',
                     to='contenttypes.ContentType',
                     verbose_name='Тип согласующего')),
            ],
            options={
                'verbose_name': 'Согласующий на этапе маршрута',
                'verbose_name_plural': 'Согласующие на этапах маршрутов',
            },
            bases=(RootObjectMixin, models.Model),
        ),
        migrations.CreateModel(
            name='RouteTemplatePhase',
            fields=[
                ('id',
                 models.AutoField(
                     auto_created=True,
                     primary_key=True,
                     serialize=False,
                     verbose_name='ID')),
                ('number',
                 models.PositiveSmallIntegerField(
                     verbose_name='Номер этапа в шаблоне')),
                ('name',
                 models.CharField(
                     max_length=255, verbose_name='Наименование этапа')),
                ('deadline',
                 models.PositiveSmallIntegerField(
                     blank=True,
                     help_text='Указывается число рабочих дней',
                     null=True,
                     verbose_name='Нормативный срок исполнения')),
                ('template',
                 models.ForeignKey(
                     on_delete=CASCADE,
                     related_name='phases',
                     to='m3_object_coordination.RouteTemplate',
                     verbose_name='Шаблон маршрута')),
            ],
            options={
                'verbose_name': 'Этап шаблона в маршруте',
                'verbose_name_plural': 'Этапы шаблона в маршруте',
            },
        ),
        migrations.AddField(
            model_name='routetemplateapproover',
            name='phase',
            field=models.ForeignKey(
                on_delete=CASCADE,
                related_name='approovers',
                to='m3_object_coordination.RouteTemplatePhase',
                verbose_name='Этап маршрута'),
        ),
        migrations.AddField(
            model_name='routephase',
            name='template',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=SET_NULL,
                related_name='+',
                to='m3_object_coordination.RouteTemplatePhase',
                verbose_name='Шаблон этапа'),
        ),
        migrations.AddField(
            model_name='routeapproover',
            name='phase',
            field=models.ForeignKey(
                on_delete=CASCADE,
                related_name='approovers',
                to='m3_object_coordination.RoutePhase',
                verbose_name='Этап маршрута'),
        ),
        migrations.AddField(
            model_name='routeapproover',
            name='template',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=SET_NULL,
                related_name='+',
                to='m3_object_coordination.RouteTemplateApproover',
                verbose_name='Согласующий на этапе шаблона маршрута'),
        ),
        migrations.AddField(
            model_name='route',
            name='template',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=SET_NULL,
                related_name='routes',
                to='m3_object_coordination.RouteTemplate',
                verbose_name='Шаблон маршрута'),
        ),
        migrations.AddField(
            model_name='log',
            name='approover',
            field=models.ForeignKey(
                on_delete=CASCADE,
                related_name='log_records',
                to='m3_object_coordination.RouteApproover',
                verbose_name='Согласующий'),
        ),
        migrations.AddField(
            model_name='log',
            name='user_type',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=CASCADE,
                related_name='+',
                to='contenttypes.ContentType'),
        ),
        migrations.AlterUniqueTogether(
            name='routetemplatephase',
            unique_together=set([('template', 'number')]),
        ),
        migrations.AlterUniqueTogether(
            name='routetemplateapproover',
            unique_together=set([('phase', 'approover_type', 'approover_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='routephase',
            unique_together=set([('route', 'number')]),
        ),
        migrations.AlterUniqueTogether(
            name='routeapproover',
            unique_together=set([('phase', 'approover_type', 'approover_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='route',
            unique_together=set([('object_type', 'object_id')]),
        ),
    ]
