import os
from uuid import (
    uuid1,
)

from django.db import (
    models,
)

from educommon.audit_log.models import (
    LoggableModelMixin,
)
from m3.db import (
    BaseObjectModel,
)

from edu_eldoc_registry.base_models import (
    DateAwareModel,
)
from edu_eldoc_registry.enums import (
    DocumentStatus,
)
from edu_eldoc_registry.paths import (
    upload_doc_to_path,
    upload_sign_to_path,
)


class Document(LoggableModelMixin, BaseObjectModel, DateAwareModel):
    """
    Документ для подписания
    """

    uuid = models.UUIDField(default=uuid1, editable=False, unique=True)
    name = models.CharField(max_length=255, verbose_name='Название файла')
    file = models.FileField(
        upload_to=upload_doc_to_path,
        max_length=255,
        verbose_name='Файл для подписания'
    )

    status = models.SmallIntegerField(
        choices=DocumentStatus.get_choices(),
        # По умолчанию "Готов к подписанию", 
        # так как в большинстве случаев документ 
        # сразу готов к подписанию
        default=DocumentStatus.READY.id,
    )

    class Meta:
        verbose_name = 'Электронный документ'
        verbose_name_plural = 'Электронные документы'


class Certificate(LoggableModelMixin, BaseObjectModel, DateAwareModel):
    """
    Сертификат подписания
    """
    serial = models.CharField(
        max_length=64,
        verbose_name='Серийный номер',
        unique=True
    )

    name = models.CharField(
        max_length=255,
        verbose_name='Название сертификата'
    )

    subject = models.CharField(
        max_length=255,
        verbose_name='Владелец'
    )

    issuer = models.CharField(
        max_length=255,
        verbose_name='Издатель'
    )

    date_from = models.DateTimeField(
        verbose_name='Действителен с'
    )

    date_to = models.DateTimeField(
        verbose_name='Действителен до'
    )

    class Meta:
        verbose_name = 'Информация о сертификате'
        verbose_name_plural = 'Информация о сертификатах'


class Sign(LoggableModelMixin, BaseObjectModel, DateAwareModel):
    """
    Подпись документа

    Поддерживается добавление нескольких подписей к одному документу
    Каждая подпись будет храниться в своей папке с названием uuid
    
    Контролировать кол-во подписей лучше статусом документа, 
    и переводить его в статус "Подписано" если нельзя больше 
    добавлять новые подписи
    """
    uuid = models.UUIDField(default=uuid1, editable=False, unique=True)

    document = models.ForeignKey(
        Document,
        verbose_name='Подписанный документ',
        on_delete=models.PROTECT
    )

    certificate = models.ForeignKey(
        Certificate,
        verbose_name='Подписан сертификатом',
        on_delete=models.PROTECT
    )

    sign_file = models.FileField(
        upload_to=upload_sign_to_path,
        max_length=255, 
        verbose_name='Файл подписи'
    )

    attached = models.BooleanField(
        verbose_name="Присоединенная подпись"
    )

    @property
    def name(self) -> str:
        return os.path.basename(self.sign_file.name)

    class Meta:
        verbose_name = 'Подпись документа'
        verbose_name_plural = 'Подписи документов'
