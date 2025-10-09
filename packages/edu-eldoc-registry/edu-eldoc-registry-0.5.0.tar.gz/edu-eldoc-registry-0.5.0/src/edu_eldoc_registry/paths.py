import os
from typing import (
    TYPE_CHECKING,
)

from django.conf import (
    settings,
)


if TYPE_CHECKING:
    from edu_eldoc_registry.models import (
        Document,
        Sign,
    )


def get_document_path(file_name: str, extension: str, *directory: str) -> str:
    """
    Получение пути для файла

    :param file_name: Название файла
    :param extension: Расширение файла
    :param directory: Вложенные папки
    :returns: Путь для файла
    """
    path = [
        settings.SIGN_DOCUMENT_STORE_PATH,
        *directory,
        f'{file_name}{extension}',
    ]

    return os.path.join(*path)


def upload_doc_to_path(instance: 'Document', file_name: str) -> str:
    """
    Хэлпер для поля Document.file
    """
    file_name, extension = os.path.splitext(file_name)
    return get_document_path(file_name, extension, instance.uuid.hex)


def upload_sign_to_path(instance: 'Sign', file_name: str) -> str:
    """
    Хэлпер для поля Sing.sign_file
    """
    file_name, extension = os.path.splitext(file_name)
    return get_document_path(
        file_name, extension, instance.document.uuid.hex, instance.uuid.hex)
