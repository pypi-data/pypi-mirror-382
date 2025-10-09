"""
Модуль содержит "небезопасные" функции, которые могут нарушать целостность 
данных или предоставляют функционал который не должен быть доступен конечным 
пользователям
"""
from __future__ import (
    annotations,
)

import base64
import os

from django.core.files.base import (
    ContentFile,
)
from django.db.transaction import (
    atomic,
)

from edu_eldoc_registry.constants import (
    EXT_SIG,
)
from edu_eldoc_registry.exceptions import (
    SignException,
)
from edu_eldoc_registry.models import (
    Certificate,
    Document,
    Sign,
)


def add_sign(doc: Document, 
             sign_data: str, 
             attached: bool, 
             cert: Certificate, 
             sign_extension: str = EXT_SIG
             ) -> Sign:
    """
    Добавление подписи к документу

    "Небезопасна" так как просто добавляет подпись 
    без проверки и смены статуса документа
    
    Для безопасного добавления подписи следует использовать 
    `api.common.sign_document` 
    
    :param doc: Документ для подписания
    :param sign_data: Подпись в формате base64
    :param attached: Признак прикреплённой подписи
    :param cert: Сертификат подписания
    :param sign_extension: Расширение для файла с подписью
    :returns: Объект файла подписи
    """
    doc_filename = os.path.basename(doc.file.name)

    sign_file = ContentFile(
        base64.b64decode(sign_data), name=f'{doc_filename}.{sign_extension}'
    )

    if Sign.objects.filter(document=doc, certificate=cert).exists():
        raise SignException('Документ уже был подписан данным сертификатом')
    
    return Sign.objects.create(
        document=doc,
        certificate=cert,
        sign_file=sign_file,
        attached=attached
    )


@atomic
def revoke_sign(sign: Sign, keep_file: bool = True) -> None:
    """
    Удалить подпись документа

    Функция исключительно для некорректных подписей и нужд разработки, 
    процедура отзыва подписи для конечных пользователей не предусмотренна

    :param sign: Объект подписи
    :param keep_file: Оставлять ли файл подписи
    """
    sign_dir = os.path.dirname(sign.sign_file.path)
    sign.delete()

    if not keep_file:
        os.remove(sign.sign_file.path)
        os.rmdir(sign_dir)
