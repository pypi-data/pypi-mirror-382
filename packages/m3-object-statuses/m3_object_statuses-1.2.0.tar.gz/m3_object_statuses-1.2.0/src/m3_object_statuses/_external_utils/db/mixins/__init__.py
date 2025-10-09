# coding: utf-8
"""Классы-примеси для моделей Django."""
from typing import Callable
from typing import NoReturn

from django.db import models
from django.db.transaction import atomic


class DeferredActionsMixin(models.Model):

    """Класс-примесь для выполнения отложенных действий в моделях.

    Позволяет выполнять действия, оформленные в виде callable-объектов,
    до/после сохранения/удаления объекта модели.

    .. code-block:: python

       class TestModel(DeferredActionsMixin, BaseModel):
           def simple_clean(self, errors):
               super().simple_clean()

               if self.status_id != get_original_object(self).status_id:
                   log = Log.objects.create(
                       object_id=self.id,
                   )
                   log.full_clean()
                   self.after_save(log.save)
    """

    class Meta:  # noqa: D106
        abstract = True

    def __init__(self, *args, **kwargs):  # noqa: D107
        super().__init__(*args, **kwargs)

        self.__pre_save_actions = []
        self.__post_save_actions = []
        self.__pre_delete_actions = []
        self.__post_delete_actions = []

    def before_save(self, action: Callable) -> NoReturn:
        """Добавляет действие, которое будет выполнено ДО сохранения."""
        self.__pre_save_actions.append(action)

    def after_save(self, action: Callable) -> NoReturn:
        """Добавляет действие, которое будет выполнено ПОСЛЕ сохранения."""
        self.__post_save_actions.append(action)

    def before_delete(self, action: Callable) -> NoReturn:
        """Добавляет действие, которое будет выполнено ДО удаления."""
        self.__pre_delete_actions.append(action)

    def after_delete(self, action: Callable) -> NoReturn:
        """Добавляет действие, которое будет выполнено ПОСЛЕ удаления."""
        self.__post_delete_actions.append(action)

    @staticmethod
    def __execute_actions(actions):
        """Выполняет запланированные ранее действия."""
        while actions:
            action = actions.pop()
            action()

    @atomic
    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """Дополняет сохранение объекта выполнением запланированных действий.

        Действия, выполняемые **до** и **после** сохранения добавляются с
        помощью методов :meth:`before_save` и :meth:`after_save`
        соответственно.
        """
        self.__execute_actions(self.__pre_save_actions)
        super().save(*args, **kwargs)
        self.__execute_actions(self.__post_save_actions)

    @atomic
    def delete(self, *args, **kwargs):  # pylint: disable=arguments-differ
        """Дополняет удаление объекта выполнением запланированных действий.

        Действия, выполняемые **до** и **после** удаления добавляются с
        помощью методов :meth:`before_delete` и :meth:`after_delete`
        соответственно.
        """
        self.__execute_actions(self.__pre_delete_actions)
        result = super().delete(*args, **kwargs)
        self.__execute_actions(self.__post_delete_actions)
        return result

    @atomic
    def safe_delete(self, *args, **kwargs):
        """Дополняет удаление объекта выполнением запланированных действий.

        Действия, выполняемые **до** и **после** удаления добавляются с
        помощью методов :meth:`before_delete` и :meth:`after_delete`
        соответственно.
        """
        self.__execute_actions(self.__pre_delete_actions)
        result = super().safe_delete(*args, **kwargs)
        self.__execute_actions(self.__post_delete_actions)
        return result


class StringFieldsCleanerMixin(models.Model):

    """Примесь для удаления из строковых полей модели лишних пробелов.

    Во всех текстовых полях модели удаляет пробельные символы в начале и конце
    строки, несколько идущих подряд пробелов заменяет на один.

    Для полей с разрешенными пустыми значениями (null=True) пустые строки
    заменяет на None.

    .. note::
       В документации Django текстовых полей не рекомендуется использовать
       значение *None*, т.к. в этом случае возникает неоднозначность - пустым
       значением будет являться не только None, но и пустая строка. Подробнее
       см. http://djbook.ru/rel1.4/ref/models/fields.html#null. Но
       использование пустой строки совместно с ограничением уникальности
       приводит к невозможности сохранения более одной записи с пустым
       значением, поэтому для однозначности в текстовых полях будем
       использовать значение None, если указано null=True, и пустую строку в
       остальных случаях.
    """

    def clean_fields(self, exclude=None):  # :noqa: D102
        for field in self._meta.fields:
            if isinstance(field, (models.TextField, models.CharField)):
                field_value = getattr(self, field.attname)

                if field_value is not None:
                    field_value = str(field_value).strip()
                    # Удаление лишних пробелов
                    while field_value.find('  ') != -1:
                        field_value = field_value.replace('  ', ' ')

                if not field_value:
                    field_value = None if field.null else ''

                setattr(self, field.attname, field_value)

        return super(StringFieldsCleanerMixin, self).clean_fields(exclude)

    class Meta:  # :noqa: D106
        abstract = True
