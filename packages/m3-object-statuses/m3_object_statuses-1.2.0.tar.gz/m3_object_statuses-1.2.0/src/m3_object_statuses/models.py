# coding: utf-8
# pylint: disable=arguments-differ, protected-access
from datetime import datetime
from typing import DefaultDict
from typing import Iterable
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Union

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import NON_FIELD_ERRORS
from django.db import models
from django.db.models.base import Model
from django.db.models.base import ModelBase
from django.db.models.deletion import CASCADE
from django.db.models.deletion import PROTECT
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.db.models.signals import post_delete
from django.db.transaction import atomic
from django.dispatch.dispatcher import receiver
from m3.actions.exceptions import ApplicationLogicException

import m3_object_statuses

from ._external_utils.db.mixins.validation import Manager
from ._external_utils.db.mixins.validation import ModelValidationMixin
from ._external_utils.db.mixins.validation import post_clean
from ._external_utils.db.models import BaseModel
from ._external_utils.utils.db import get_original_object
from ._external_utils.utils.db import is_object_changed
from ._external_utils.utils.misc import cached_property
from .signals import post_status_change
from .signals import pre_status_change


ErrorsDict = DefaultDict[str, List[str]]
# -----------------------------------------------------------------------------


class StatusMixin(ModelValidationMixin, Model):

    """Класс-примесь к моделям объектов со статусами.

    Обеспечивает:

        - наличие поля "Статус" (status);
        - контроль допустимости статусов;
        - контроль допустимости смены статуса;
        - ведение истории изменения статусов объектов.
    """

    status = models.ForeignKey(
        'm3_object_statuses.Status',
        verbose_name='Статус объекта',
        on_delete=PROTECT,
        related_name='+',
    )

    class Meta:  # noqa: D106
        abstract = True

    def clean_fields(self, *args, **kwargs) -> NoReturn:  # noqa: D102
        # Заполнение статуса для новых объектов.
        if not self.status_id:
            self.status = Status.objects.get_default_for_model(self)

        super().clean_fields(*args, **kwargs)

    @atomic
    def save(self, user: Optional[Model] = None, *args, **kwargs) -> NoReturn:
        r"""Дополняет сохранение объекта отправкой сигналов о смене статуса.

        :param user: Пользователь, который изменил статус объекта.

        .. seealso::

           Описание сигналов :obj:`~m3_object_statuses.signals.\
           pre_status_change` и :obj:`~m3_object_statuses.signals.\
           post_status_change`.
        """
        original_object = get_original_object(self)
        src_status_id = original_object.status_id if original_object else None
        dst_status_id = self.status_id

        success = True
        error_messages = []
        if src_status_id != dst_status_id:
            src_status = (
                Status.objects.get(pk=src_status_id) if src_status_id else None
            )
            dst_status = (
                Status.objects.get(pk=dst_status_id) if dst_status_id else None
            )

            success = True
            for _, response in pre_status_change.send(
                sender=self.__class__,
                instance=self,
                src_status=src_status,
                dst_status=dst_status,
                user=user,
            ):
                if isinstance(response, str):
                    error_messages.append(response)
                    success = False

        config = m3_object_statuses.config.ignore_unsuccessful_transitions
        key = self._meta.app_label + '.' + self._meta.object_name
        if success or not config.get(key, config.get(None, True)):
            super().save(*args, **kwargs)

        if src_status_id != dst_status_id:
            post_status_change.send(
                sender=self.__class__,
                instance=self,
                src_status=src_status,
                dst_status=dst_status,
                user=user,
                success=success,
                error_messages=error_messages,
            )

    @atomic
    def delete(self, *args, **kwargs):  # noqa: D102
        # Переопределяется в связи с тем, что в StatusTransition
        # удаляются связанные записи, поэтому нужна транзакция.
        return super().delete(*args, **kwargs)
# -----------------------------------------------------------------------------


class _ObjectTypeMixin(ModelValidationMixin):

    """Класс-примесь для моделей, ссылающихся на тип объекта.

    Предоставляет поле ``object_type`` для хранения типа объектов, а также
    проверку допустимости использования статусов для этого типа объектов.
    """

    object_type = models.ForeignKey(
        ContentType,
        verbose_name='Тип объекта',
        related_name='+',
        on_delete=PROTECT,
    )

    class Meta:
        abstract = True

    def simple_clean(self, errors: ErrorsDict):
        super().simple_clean(errors)

        # Проверка допустимости использования статусов для типа объектов.
        if 'object_type' not in errors:
            model_class = self.object_type.model_class()
            if not issubclass(model_class, StatusMixin):
                errors['object_type'].append(
                    'Недопустимый тип объектов: {}.'
                    .format(model_class._meta.verbose_name)
                )
# -----------------------------------------------------------------------------


class StatusManager(Manager):

    """Менеджер модели справочника "Статусы"."""

    def get_by_natural_key(self, code) -> 'Status':  # noqa: D102
        return self.get(code=code)

    def get_for_model(self, model: Union[ModelBase, StatusMixin]) -> QuerySet:
        """Возвращает статусы для указанной модели."""
        object_type = ContentType.objects.get_for_model(model)
        assert issubclass(object_type.model_class(), StatusMixin), model

        return self.model.objects.filter(
            pk__in=ObjectTypeStatus.objects.filter(
                object_type=object_type,
            ).values('status')
        )

    @staticmethod
    def get_default_for_model(
        model: Union[ModelBase, StatusMixin]
    ) -> Optional['Status']:
        """Возвращает статус по умолчанию для указанной модели."""
        object_type_status = ObjectTypeStatus.objects.filter(
            object_type=ContentType.objects.get_for_model(model),
            is_default=True,
        ).first()
        return object_type_status.status if object_type_status else None


class Status(BaseModel):

    """Справочник "Статусы".

    Содержит коды и наименования используемых в Системе статусов.

    Заполнение данными предполагается через миграции. Один и тот же статус
    может быть использован для объектов разных типов.
    """

    code = models.CharField(
        'Код',
        max_length=20,
        unique=True,
    )
    name = models.CharField(
        'Наименование',
        max_length=100,
    )

    objects = StatusManager()

    class Meta:  # noqa: D106
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'

    def natural_key(self):  # noqa: D102
        return (self.code,)
# -----------------------------------------------------------------------------


class ObjectTypeStatusManager(Manager):

    """Менеджер модели "Допустимые для типов объектов статусы"."""

    def get_by_natural_key(
        self,
        app_label: str,
        model_name: str,
        status_code: str
    ) -> 'ObjectTypeStatus':  # noqa: D102
        object_type = ContentType.objects.get_by_natural_key(
            app_label, model_name
        )
        status = Status.objects.get_by_natural_key(status_code)
        return self.get(
            object_type=object_type,
            status=status,
        )

    def is_valid_for(self,
                     status: Union[int, Status],
                     model: Union[ModelBase, StatusMixin]) -> bool:
        """Возвращает True, если статус допустим для объектов модели.

        :raises TypeError: при передаче значений аргументов с некорректными
            типами данных.
        :raises ValueError: при передаче некорректных значений аргументов.
        """
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        if isinstance(status, int):
            status_id = status
        elif isinstance(status, Status):
            status_id = status.pk
        else:
            raise TypeError(
                'Неподдерживаемый тип данных аргумента status.', status
            )

        if not status_id:
            raise ValueError(
                'Некорректный идентификатор статуса.', status_id
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        object_type = ContentType.objects.get_for_model(model)
        if not issubclass(object_type.model_class(), StatusMixin):
            raise TypeError(
                'Некорректный тип данных аргумента model.', model
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        result = self.filter(
            object_type=object_type,
            status=status_id,
        ).exists()

        return result
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    @staticmethod
    @receiver(post_clean)
    def _check_is_default_field(instance, errors, **_):
        """Проверяет, что для модели указан только один статус по умолчанию."""
        if (
            'object_type' in errors or
            # sender в @receiver не используется, т.к. он еще не определен.
            not isinstance(instance, ObjectTypeStatus) or
            not instance.is_default
        ):
            return

        query = ObjectTypeStatus.objects.filter(
            object_type_id=instance.object_type_id,
            is_default=True,
        )
        if instance.pk:
            query = query.exclude(pk=instance.pk)

        if query.exists():
            errors['is_default'].append(
                'Для объектов типа "{}" уже задан статус по умолчанию: "{}".'
                .format(
                    instance.object_type.model_class()._meta.verbose_name,
                    query.values_list('status__name', flat=True).first(),
                )
            )

    @staticmethod
    @receiver(post_clean)
    def _check_status_object(instance, sender, errors, **_):
        """Проверяет допустимость использования статуса для объекта."""
        if not issubclass(sender, StatusMixin) or 'status' in errors:
            return

        query = ObjectTypeStatus.objects.filter(
            object_type=ContentType.objects.get_for_model(sender),
            status_id=instance.status_id,
        )

        if instance.pk and not query.exists():
            errors['status'].append(
                f'Статус "{instance.status.name}" не может использоваться для '
                f'объектов типа "{sender._meta.verbose_name}".'
            )
        elif not instance.pk and not query.filter(
            can_be_initial=True,
        ).exists():
            errors['status'].append(
                f'Статус "{instance.status.name}" не может использоваться при '
                f'создании объектов типа "{sender._meta.verbose_name}".'
            )


class ObjectTypeStatus(_ObjectTypeMixin, BaseModel):

    """Модель "Допустимые для типов объектов статусы".

    Определяет, какие статусы можно назначать типу объекта.
    """

    status = models.ForeignKey(
        Status,
        verbose_name='Статус',
        related_name='+',
        on_delete=PROTECT,
    )
    is_default = models.BooleanField(
        'Статус по умолчанию',
        default=False,
    )
    can_be_initial = models.BooleanField(
        'Может быть использован при создании объекта',
        default=False,
    )
    action_text = models.CharField(
        'Текст для контрола перевода в статус',
        max_length=100,
        null=True, blank=True,
    )

    objects = ObjectTypeStatusManager()

    class Meta:  # noqa: D106
        unique_together = ('object_type', 'status')
        verbose_name = 'Допустимый для типа объектов статус'
        verbose_name_plural = 'Допустимые для типов объектов статусы'

    def natural_key(self):  # noqa: D102
        return self.object_type.natural_key() + self.status.natural_key()

    @atomic
    def delete(self, *args, **kwargs):  # noqa: D102
        # Переопределяется в связи с тем, что в ValidStatusTransition
        # удаляются связанные записи, поэтому нужна транзакция.
        return super().delete(*args, **kwargs)
# -----------------------------------------------------------------------------


class ValidStatusTransitionManager(Manager):

    """Менеджер модели "Допустимые для типа объектов переходы статусов"."""

    def get_by_natural_key(
        self,
        app_label: str,
        model_name: str,
        src_status_code: str,
        dst_status_code: str
    ) -> 'ValidStatusTransition':  # noqa: D102
        object_type = ContentType.objects.get_by_natural_key(
            app_label, model_name
        )
        src_status = Status.objects.get_by_natural_key(src_status_code)
        dst_status = Status.objects.get_by_natural_key(dst_status_code)
        return self.get(
            object_type=object_type,
            src_status=src_status,
            dst_status=dst_status,
        )

    @staticmethod
    @receiver(post_delete, sender=ObjectTypeStatus)
    def __on_object_type_status_delete(instance, **_):
        """Удаление переходов при удалении связи статуса и типа объекта."""
        ValidStatusTransition.objects.filter(
            Q(
                src_status_id=instance.status_id
            ) | Q(
                dst_status_id=instance.status_id
            ),
            object_type_id=instance.object_type_id,
        ).delete()

    @staticmethod
    @receiver(post_clean, sender=ObjectTypeStatus)
    def __check_object_type_status_change(instance, errors, **_):
        """Проверяет связь типа объекта и статуса при изменении.

        Предотвращает изменение значений полей ``object_type`` и ``status`` в
        модели :class:`~m3_object_statuses.models.ObjectTypeStatus`, если для
        них определен допустимый преход статуса.
        """
        original = get_original_object(instance)
        if (
            original and
            (
                instance.object_type_id != original.object_type_id or
                instance.status_id != original.status_id
            ) and
            ValidStatusTransition.objects.filter(
                Q(
                    src_status_id=original.status_id
                ) | Q(
                    dst_status_id=original.status_id
                ),
                object_type_id=original.object_type_id,
            ).exists()
        ):
            object_name = getattr(instance, '_meta').verbose_name
            errors[NON_FIELD_ERRORS].append(
                f'Изменение записи в модели "{object_name}" невозможно, т.к. '
                'для неё прописаны допустимые переходы статусов.'
            )

    @staticmethod
    @receiver(post_clean)
    def _check_status_transition(instance, errors, **_):
        """Проверяет допустимость смены статуса объекта."""
        if not isinstance(instance, StatusMixin):
            return

        original_object = get_original_object(instance)
        if not original_object:
            return

        src_status_id = original_object.status_id
        dst_status_id = instance.status_id

        if src_status_id == dst_status_id:
            return

        if not ValidStatusTransition.objects.filter(
            object_type=ContentType.objects.get_for_model(instance),
            src_status_id=src_status_id,
            dst_status_id=dst_status_id,
        ).exists():
            object_name = getattr(instance, '_meta').verbose_name

            src_status_name = Status.objects.filter(
                pk=src_status_id,
            ).values_list('name', flat=True).first()
            dst_status_name = Status.objects.filter(
                pk=dst_status_id,
            ).values_list('name', flat=True).first()

            errors['status'].append(
                f'Для объектов типа "{object_name}" смена статуса с '
                f'"{src_status_name}" на "{dst_status_name}" недопустима.'
            )


class ValidStatusTransition(_ObjectTypeMixin, BaseModel):

    """Допустимые для типа объектов переходы статусов.

    Если для типа объектов (``object_type``) прописаны допустимые переходы
    статусов, то смена статусов объектов этого типа будет ограничена только
    этими переходами. Если же допустимые переходы не определяются, то смена
    статусов объектов не контролируется.
    """

    src_status = models.ForeignKey(
        Status,
        verbose_name='Текущий статус',
        related_name='+',
        on_delete=CASCADE,
    )
    dst_status = models.ForeignKey(
        Status,
        verbose_name='Следующий статус',
        related_name='+',
        on_delete=CASCADE,
    )
    action_text = models.CharField(
        'Текст для контрола перевода в статус',
        max_length=100,
        null=True,
        blank=True
    )

    objects = ValidStatusTransitionManager()

    class Meta:  # noqa: D106
        verbose_name = 'Допустимый переход между статусами объектов'
        verbose_name_plural = 'Допустимые переходы между статусами объектов'
        unique_together = ('object_type', 'src_status', 'dst_status')

    def natural_key(self):  # noqa: D102
        return (
            self.object_type.natural_key() +
            self.src_status.natural_key() +
            self.dst_status.natural_key()
        )

    def simple_clean(self, errors: ErrorsDict):  # noqa: D102
        super().simple_clean(errors)

        # Проверка допустимости статусов для указанного типа объектов.
        for status_field_name in ('src_status', 'dst_status'):
            status_id = getattr(self, status_field_name + '_id')
            if self.object_type_id and status_id:
                if not ObjectTypeStatus.objects.filter(
                    object_type_id=self.object_type_id,
                    status_id=status_id,
                ).exists():
                    # pylint: disable=protected-access
                    errors[status_field_name].append(
                        'Статус "{}" не доступен для объекта "{}".'.format(
                            getattr(self, status_field_name).name,
                            self.object_type.model_class()._meta.verbose_name,
                        )
                    )
# -----------------------------------------------------------------------------


class StatusTransitionManager(Manager):

    """Менеджер объектов модели ``StatusHistory``."""

    def for_object(self, obj: StatusMixin) -> QuerySet:
        """Возвращает запрос на выборку истории указанного объекта.

        :param obj: Объект со статусом.
        """
        if obj.pk:
            object_type = ContentType.objects.get_for_model(obj)
            result = self.filter(
                object_type=object_type,
                object_id=obj.pk,
            )
        else:
            result = self.none()

        return result

    @staticmethod
    @receiver(post_delete)
    def __clear_history(instance, **__):
        """Удаляет историю изменения статусов объектов при их удалении."""
        if isinstance(instance, StatusMixin):
            StatusTransition.objects.filter(
                object_type=ContentType.objects.get_for_model(instance),
                object_id=instance.pk,
            ).delete()

    @staticmethod
    @receiver(post_status_change)
    def _log_status_change(
        instance: StatusMixin,
        dst_status: Status,
        user: Model,
        success: bool,
        error_messages: Iterable[str],
        **_
    ) -> NoReturn:
        """Сохраняет в истории данные об изменении статуса объекта."""
        if isinstance(instance, StatusMixin) and instance.pk is not None:
            StatusTransition.objects.create(
                object_type=ContentType.objects.get_for_model(instance),
                object_id=instance.pk,
                user_type=(
                    ContentType.objects.get_for_model(user)
                    if user
                    else None
                ),
                user_id=user.pk if user else None,
                status=dst_status,
                success=success,
                error_message=', '.join(error_messages),
            )


class StatusTransition(_ObjectTypeMixin, BaseModel):

    """История изменения статусов объектов."""

    object_id = models.IntegerField(
        'Идентификатор объекта',
    )
    object = GenericForeignKey('object_type', 'object_id')

    user_type = models.ForeignKey(
        ContentType,
        verbose_name='Модель пользователя',
        related_name='+',
        on_delete=PROTECT,
        blank=True, null=True,
    )
    user_id = models.IntegerField(
        'Идентификатор пользователя',
        blank=True, null=True,
    )
    user = GenericForeignKey('object_type', 'object_id')

    status = models.ForeignKey(
        Status,
        verbose_name='Новый статус',
        related_name='+',
        on_delete=PROTECT,
    )
    changed_at = models.DateTimeField(
        'Временная метка',
        default=datetime.now,
    )
    success = models.BooleanField(
        'Успешность попытки смены статуса',
        default=True,
    )
    error_message = models.TextField(
        'Текст сообщения об ошибке',
        null=True,
        blank=True
    )

    objects = StatusTransitionManager()

    class Meta:  # noqa: D106
        verbose_name = 'Смена статуса объекта'
        verbose_name_plural = 'История изменения статусов объектов'
        ordering = ('changed_at',)
        index_together = (
            ('object_type', 'object_id'),
        )

    def __get_history(self) -> Union[QuerySet, None]:
        result = None

        if (
            self.object_type_id and
            self.object_id and
            self.changed_at
        ):
            result = StatusTransition.objects.filter(
                object_type_id=self.object_type_id,
                object_id=self.object_id,
            ).order_by('changed_at')

        return result

    @cached_property
    def previous(self):
        """Предыдущий статус.

        :rtype: tkp_rkm.directories.prefix.models.StatusHistory
        """
        result = None

        query = self.__get_history()
        if query is not None:
            result = query.filter(
                changed_at__lt=self.changed_at,
            ).last()

        return result

    @cached_property
    def next(self):
        """Следующий статус.

        :rtype: tkp_rkm.directories.prefix.models.StatusHistory
        """
        result = None

        query = self.__get_history()
        if query is not None:
            result = query.filter(
                changed_at__gt=self.changed_at,
            ).first()

        return result

    def simple_clean(self, errors: ErrorsDict):  # noqa: D102
        super().simple_clean(errors)

        if 'object_type' in errors or 'status' in errors:
            return

        if self.pk:
            if is_object_changed(self):
                errors[NON_FIELD_ERRORS].append(
                    'Изменение записей в истории переходов статусов '
                    'недопустимо.'
                )
            else:
                return

        object_model = self.object_type.model_class()
        object_name = getattr(object_model, '_meta').verbose_name
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка наличия объекта в БД.

        if (
            self.object_id and
            not object_model.objects.filter(pk=self.object_id).exists()
        ):
            errors['object_id'].append(
                f'Объект не существует: "{object_name}", ID={self.object_id}.'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка наличия пользователя в БД.

        if (
            'user_type' not in 'errors' and
            self.user_type_id and
            not self.user_type.model_class().objects.filter(
                pk=self.user_id,
            ).exists()
        ):
            pass
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
        # Проверка допустимости статуса для типа объектов.

        if (
            'object_type' not in errors and
            'status' not in errors and
            not ObjectTypeStatus.objects.filter(
                object_type_id=self.object_type_id,
                status_id=self.status_id,
            ).exists()
        ):
            errors['status'].append(
                f'Статус "{self.status.name}" не доступен  для объекта '
                f'"{object_name}".'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

        # Проверка наличия следующих записей в истории (их не должно быть).
        if self.next:
            errors[NON_FIELD_ERRORS].append(
                'Добавление записей в середину истории недопустимо.'
            )

        # Проверка допустимости перехода статусов.
        if (
            self.previous and
            not ValidStatusTransition.objects.filter(
                object_type_id=self.object_type_id,
                src_status=self.previous.status,
                dst_status=self.status,
            ).exists()
        ):
            errors['status'].append(
                f'Для объектов типа "{object_name}" смена статуса с '
                f'"{self.previous.status.name}" на "{self.status.name}" '
                'недопустима.'
            )
        # - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

    def save(self, *args, **kwargs):  # noqa: D102
        if self.pk and is_object_changed(self):
            raise ApplicationLogicException(  # pragma: nocover
                'Изменение записей в истории переходов статусов недопустимо.'
            )

        super().save(*args, **kwargs)

    def delete(self, *_, **__):  # noqa: D102
        raise ApplicationLogicException(  # pragma: nocover
            'Удаление записей в истории переходов статусов недопустимо.'
        )

    def safe_delete(self):  # noqa: D102
        raise ApplicationLogicException(  # pragma: nocover
            'Удаление записей в истории переходов статусов недопустимо.'
        )
# -----------------------------------------------------------------------------
