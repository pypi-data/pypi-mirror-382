PERM_GROUP__DOC_REGISTRY = 'eldoc-doc-registry'
PERM_GROUP__CERT_REGISTRY = 'eldoc-cert-registry'

SUBPERM_VIEW = 'view'
SUBPERM_SIGN = 'sign-doc'

PERM__DOCUMENT__VIEW = f'{PERM_GROUP__DOC_REGISTRY}/{SUBPERM_VIEW}'
PERM__DOCUMENT__ADD_SIGN = f'{PERM_GROUP__DOC_REGISTRY}/{SUBPERM_SIGN}'

PERM__CERTIFICATE__VIEW = f'{PERM_GROUP__CERT_REGISTRY}/{SUBPERM_VIEW}'

permissions = (
    (PERM__DOCUMENT__VIEW,
     'Просмотр',
     'Разрешает просмотр реестра электронных документов.'),
    (PERM__DOCUMENT__ADD_SIGN,
     'Подписание',
     'Разрешает подписание электронных документов.'),
    (PERM__CERTIFICATE__VIEW,
     'Просмотр',
     'Разрешает просмотр информации о сертификатах.'),
)

groups = {
    PERM_GROUP__DOC_REGISTRY: 'Реестр электронных документов',
    PERM_GROUP__CERT_REGISTRY: 'Информация о сертификатах',
}

partitions = {
    'Реестр электронных документов': (
        PERM_GROUP__DOC_REGISTRY,
        PERM_GROUP__CERT_REGISTRY,
    ),
}
