from django.db import (
    models,
)


class CreationDateAwareModel(models.Model):
    """
    Модель сохраняющая дату создания
    """
    # момент создания записи
    created = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Создан',
    )

    class Meta:
        abstract = True


class ModificationDateAwareModel(models.Model):
    """
    Модель сохраняющая дату изменения
    """
    # момент изменения записи
    modified = models.DateTimeField(
        auto_now=True,
        db_index=True,
        verbose_name='Изменен',
    )

    class Meta:
        abstract = True


class DateAwareModel(CreationDateAwareModel, ModificationDateAwareModel):
    """
    Модель сохраняющая даты создания и изменения
    """
    class Meta:
        abstract = True
