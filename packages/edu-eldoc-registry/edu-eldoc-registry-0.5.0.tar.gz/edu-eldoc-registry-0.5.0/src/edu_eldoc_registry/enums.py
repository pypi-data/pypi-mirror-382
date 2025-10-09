from educommon.utils.enums import (
    NamedIntEnum,
)


class DocumentStatus(NamedIntEnum):
    """Статусы подписания документа."""

    NEW: 'NamedIntEnum' = 0, 'Новый'
    READY: 'NamedIntEnum' = 1, 'Готов к подписанию'
    SIGNED: 'NamedIntEnum' = 2, 'Подписан'
    REJECTED: 'NamedIntEnum' = 3, 'Отклонён'
