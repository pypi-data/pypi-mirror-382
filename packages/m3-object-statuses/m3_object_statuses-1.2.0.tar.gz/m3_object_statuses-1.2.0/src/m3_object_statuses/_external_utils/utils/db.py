# coding: utf-8
from typing import Any
from typing import Optional
from typing import Tuple
from typing import Union
from weakref import WeakKeyDictionary

from django.db.models import Model
from django.db.models.signals import post_delete
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.forms.models import model_to_dict


# -----------------------------------------------------------------------------

_original_objects_cache = WeakKeyDictionary()


def get_original_object(obj: Model) -> Union[Model, None]:
    """Возвращает загруженный из БД объект модели.

    Если первичный ключ не заполнен, либо в БД нет такого объекта, то
    возвращает None.
    """
    if obj.pk is None:
        result = None
    elif obj in _original_objects_cache:
        result = _original_objects_cache[obj]
    else:
        try:
            result = obj.__class__.objects.get(pk=obj.pk)
        except obj.__class__.DoesNotExist:
            result = None

        _original_objects_cache[obj] = result

    return result


@receiver(post_delete)
@receiver(post_save)
def _clear_cache(instance, **kwargs):  # pylint: disable=unused-argument
    """Удаляет объект из кэша функции get_original_object."""
    if instance in _original_objects_cache:
        del _original_objects_cache[instance]
# -----------------------------------------------------------------------------


def get_original_field_values(obj: Model, *field_names: str) -> Tuple[Any]:
    """Возвращает исходное значение полей."""
    assert field_names

    if obj.pk is None:
        result = None
    else:
        result = obj.__class__.objects.filter(
            pk=obj.pk,
        ).values_list(
            *field_names, flat=len(field_names) == 1
        ).first()

    return result
# -----------------------------------------------------------------------------


def is_object_changed(obj: Model) -> Optional[bool]:
    """Возвращает True, если одно из полей объекта отличается от исходного."""
    if not obj.pk:
        return None

    values = model_to_dict(obj)
    original_values = model_to_dict(get_original_object(obj))

    return values != original_values
# -----------------------------------------------------------------------------
