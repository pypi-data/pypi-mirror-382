# coding: utf-8
from django.db.models.signals import ModelSignal


#: Сигнал о предстоящей смене статуса объекта.
#:
#: Отправляется перед созданием объекта со стаусом, либо при изменении статуса
#: объекта. При создании объекта параметр ``src_status`` сигнала будет иметь
#: значение ``None``. Отправка сигнала осуществляется из метода
#: :meth:`m3_object_statuses.models.StatusMixin.save`.
#:
#: Обработчики сигнала могут вернуть значение ``False``. В этом случае в
#: историю смены статусов объекта запись будет добавлена с признаком неудачного
#: перехода (значение поля ``success`` модели :class:`~m3_object_statuses.\
#: models.StatusTransition` будет равно ``False``), а сохранение изменений в
#: объекте выполнено не будет.
#:
#: .. seealso::
#:
#:    :meth:`~m3_object_statuses.models.StatusMixin.save`
pre_status_change = ModelSignal(
    providing_args=(
        'instance',
        'src_status',
        'dst_status',
        'user',
    ),
)

#: Сигнал о завершении попытки смены статуса объекта.
#:
#: Отправляется при попытке создания объекта со статусом, либо при смене
#: статуса объекта. В случае создания объекта параметр ``src_status`` сигнала
#: будет иметь значение ``None``. Отправка сигнала осуществляется из метода
#: :meth:`m3_object_statuses.models.StatusMixin.save`.
#:
#: .. seealso::
#:
#:    :meth:`~m3_object_statuses.models.StatusMixin.save`
post_status_change = ModelSignal(
    providing_args=(
        'instance',
        'src_status',
        'dst_status',
        'user',
        'success',
        'error_messages',
    ),
)
