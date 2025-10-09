# coding: utf-8
import datetime

from django.db import migrations
from django.db import models
from django.db.models.deletion import CASCADE
from django.db.models.deletion import PROTECT
from django.db.models.manager import Manager


class StatusManager(Manager):

    """Менеджер модели справочника "Статусы"."""

    use_in_migrations = True

    def get_by_natural_key(self, code):  # noqa: D102
        return self.get(code=code)


class ObjectTypeStatusManager(Manager):

    """Менеджер модели "Допустимые для типов объектов статусы"."""

    use_in_migrations = True

    def get_by_natural_key(self, app_label, model, status_code):  # noqa: D102
        return self.get(
            object_type__app_label=app_label,
            object_type__model=model,
            status__code=status_code,
        )


class ValidStatusTransitionManager(Manager):

    """Менеджер модели "Допустимые для типа объектов переходы статусов"."""

    use_in_migrations = True

    def get_by_natural_key(self, app_label, model, src_status_code,
                           dst_status_code):  # noqa: D102
        return self.get(
            object_type__app_label=app_label,
            object_type__model=model,
            src_status__code=src_status_code,
            dst_status__code=dst_status_code,
        )


class Migration(migrations.Migration):  # noqa: D101

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='ObjectTypeStatus',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('is_default', models.BooleanField(
                    default=False,
                    verbose_name='Статус по умолчанию',
                )),
                ('can_be_initial', models.BooleanField(
                    default=False,
                    verbose_name='Может быть использован при создании объекта',
                )),
                ('action_text', models.CharField(
                    blank=True,
                    max_length=100,
                    null=True,
                    verbose_name='Текст для контрола перевода в статус',
                )),
                ('object_type', models.ForeignKey(
                    on_delete=PROTECT,
                    related_name='+',
                    to='contenttypes.ContentType',
                    verbose_name='Тип объекта',
                )),
            ],
            options={
                'verbose_name': 'Допустимый для типа объектов статус',
                'verbose_name_plural': 'Допустимые для типов объектов статусы',
            },
            managers=(
                ('objects', ObjectTypeStatusManager()),
            ),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('code', models.CharField(
                    max_length=20,
                    unique=True,
                    verbose_name='Код',
                )),
                ('name', models.CharField(
                    max_length=100,
                    verbose_name='Наименование',
                )),
            ],
            options={
                'verbose_name': 'Статус',
                'verbose_name_plural': 'Статусы',
            },
            managers=(
                ('objects', StatusManager()),
            ),
        ),
        migrations.CreateModel(
            name='StatusTransition',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('object_id', models.IntegerField(
                    verbose_name='Идентификатор объекта',
                )),
                ('user_id', models.IntegerField(
                    blank=True,
                    null=True,
                    verbose_name='Идентификатор пользователя',
                )),
                ('changed_at', models.DateTimeField(
                    default=datetime.datetime.now,
                    verbose_name='Временная метка',
                )),
                ('success', models.BooleanField(
                    default=True,
                    verbose_name='Успешность попытки смены статуса',
                )),
                ('error_message', models.TextField(
                    blank=True,
                    null=True,
                    verbose_name='Текст сообщения об ошибке',
                )),
                ('object_type', models.ForeignKey(
                    on_delete=PROTECT,
                    related_name='+',
                    to='contenttypes.ContentType',
                    verbose_name='Тип объекта',
                )),
                ('status', models.ForeignKey(
                    on_delete=PROTECT,
                    related_name='+',
                    to='m3_object_statuses.Status',
                    verbose_name='Новый статус',
                )),
                ('user_type', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=PROTECT,
                    related_name='+',
                    to='contenttypes.ContentType',
                    verbose_name='Модель пользователя',
                )),
            ],
            options={
                'verbose_name': 'Смена статуса объекта',
                'verbose_name_plural': 'История изменения статусов объектов',
                'ordering': ('changed_at',),
            },
        ),
        migrations.CreateModel(
            name='ValidStatusTransition',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('action_text', models.CharField(
                    blank=True,
                    max_length=100,
                    null=True,
                    verbose_name='Текст для контрола перевода в статус',
                )),
                ('dst_status', models.ForeignKey(
                    on_delete=CASCADE,
                    related_name='+',
                    to='m3_object_statuses.Status',
                    verbose_name='Следующий статус',
                )),
                ('object_type', models.ForeignKey(
                    on_delete=PROTECT,
                    related_name='+',
                    to='contenttypes.ContentType',
                    verbose_name='Тип объекта',
                )),
                ('src_status', models.ForeignKey(
                    on_delete=CASCADE,
                    related_name='+',
                    to='m3_object_statuses.Status',
                    verbose_name='Текущий статус',
                )),
            ],
            options={
                'verbose_name':
                    'Допустимый переход между статусами объектов',
                'verbose_name_plural':
                    'Допустимые переходы между статусами объектов',
            },
            managers=(
                ('objects', ValidStatusTransitionManager()),
            ),
        ),
        migrations.AddField(
            model_name='objecttypestatus',
            name='status',
            field=models.ForeignKey(
                on_delete=PROTECT,
                related_name='+',
                to='m3_object_statuses.Status',
                verbose_name='Статус',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='validstatustransition',
            unique_together=set([('object_type', 'src_status', 'dst_status')]),
        ),
        migrations.AlterIndexTogether(
            name='statustransition',
            index_together=set([('object_type', 'object_id')]),
        ),
        migrations.AlterUniqueTogether(
            name='objecttypestatus',
            unique_together=set([('object_type', 'status')]),
        ),
    ]
