from datetime import (
    date,
)

from django.db.models.fields.files import (
    FieldFile,
)
from django.utils.safestring import (
    SafeString,
    mark_safe,
)


def get_download_link(file: FieldFile, text: str = 'Скачать') -> SafeString:
    """
    Получить html-ссылку на скачивание
    """
    return mark_safe(
        f'<a href="{file.url}" target="_blank">{text}</a>'
    )


def today_date_str_for_extjs() -> str:
    """
    Сегодняшняя дата в формате строки для фильтров полей в ExtJS
    """
    return f"'{date.today().strftime('%d.%m.%Y')}'"
