# coding: utf-8
from m3.db import BaseObjectModel

from .mixins import DeferredActionsMixin
from .mixins import StringFieldsCleanerMixin
from .mixins.validation import ModelValidationMixin


class BaseModel(
    DeferredActionsMixin,
    StringFieldsCleanerMixin,
    ModelValidationMixin,
    BaseObjectModel
):

    """Базовый класс для всех моделей системы."""

    class Meta:  # noqa: D106
        abstract = True
