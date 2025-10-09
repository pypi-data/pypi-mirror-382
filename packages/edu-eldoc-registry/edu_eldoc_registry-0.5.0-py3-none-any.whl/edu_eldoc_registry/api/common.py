"""
Модуль содержит общие функции для работы с пакетом
"""
from __future__ import (
    annotations,
)

from django.db.transaction import (
    atomic,
)

from edu_eldoc_registry.api.dev import (
    add_sign,
)
from edu_eldoc_registry.constants import (
    EXT_SIG,
)
from edu_eldoc_registry.enums import (
    DocumentStatus,
)
from edu_eldoc_registry.exceptions import (
    DocException,
    SignException,
)
from edu_eldoc_registry.models import (
    Certificate,
    Document,
    Sign,
)


@atomic
def sign_document(doc: Document,
                  sign_data: str,
                  attached: bool,
                  cert: Certificate,
                  sign_extension: str = EXT_SIG,
                  last_sign: bool = True
                  ) -> Sign:
    """
    Подписать документ

    :param doc: Документ для подписания
    :param sign_data: Подпись в формате base64
    :param attached: Признак прикреплённой подписи
    :param cert: Сертификат подписания
    :param sign_extension: Расширение для файла с подписью
    :param last_sign: Отметить документ подписанным по завершению
    :returns: Объект файла подписи
    """
    if doc.status != DocumentStatus.READY.id:
        raise SignException(
            'Подписать можно только документ в статусе "Готов к подписанию"')
    
    sign = add_sign(doc, sign_data, attached, cert, sign_extension)

    if last_sign:
        mark_signed(doc)

    return sign


def mark_signed(doc: Document) -> None:
    """
    Отметить документ подписанным

    :param doc: Объект документа
    """
    if doc.status != DocumentStatus.READY.id:
        raise DocException('Документ должен быть в статусе "Готов к подписанию"')

    if not Sign.objects.filter(document=doc).exists():
        raise DocException('Документ не имеет подписей')

    doc.status = DocumentStatus.SIGNED.id
    doc.save()


def mark_ready(doc: Document) -> None:
    """
    Отметить документ готовым к подписанию

    :param doc: Объект документа
    """
    if doc.status != DocumentStatus.NEW.id:
        raise DocException('Документ должен быть в статусе "Новый"')

    doc.status = DocumentStatus.READY.id
    doc.save()


def mark_rejected(doc: Document, raise_rejected: bool = True) -> None:
    """
    Отклонить документ

    :param doc: Объект документа
    :param raise_rejected: Бросать исключение если документ уже в статусе "Отклонён"
    """
    if Sign.objects.filter(document=doc).exists():
        raise DocException('Документ уже имеет подпись')

    if doc.status == DocumentStatus.REJECTED.id:
        if raise_rejected:
            raise DocException('Документ уже отклонён')
        return

    doc.status = DocumentStatus.REJECTED.id
    doc.save()
