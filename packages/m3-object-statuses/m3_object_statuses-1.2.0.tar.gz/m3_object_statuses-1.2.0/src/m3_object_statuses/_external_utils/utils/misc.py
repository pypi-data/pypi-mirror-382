# coding: utf-8
from pathlib import Path
import inspect


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
