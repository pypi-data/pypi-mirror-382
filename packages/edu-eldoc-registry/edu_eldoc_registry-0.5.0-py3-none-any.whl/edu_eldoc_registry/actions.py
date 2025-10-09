import copy
import functools
import os

from educommon.utils.ui import (
    ChoicesFilter,
    DatetimeFilterCreator,
)
from m3.actions.exceptions import (
    ApplicationLogicException,
)
from m3.actions.results import (
    OperationResult,
    PreJsonResult,
)
from m3_ext.ui.helpers import (
    mark_safe,
)
from m3_ext.ui.icons import (
    Icons,
)
from objectpack.actions import (
    BaseAction,
    BaseWindowAction,
    ObjectListWindowAction,
    ObjectPack,
    ObjectRowsAction,
)
from objectpack.filters import (
    ColumnFilterEngine,
    FilterByField,
)

from edu_eldoc_registry.api.common import (
    sign_document,
)
from edu_eldoc_registry.constants import (
    APP_VERBOSE_NAME,
    EXT_SIG,
)
from edu_eldoc_registry.enums import (
    DocumentStatus,
)
from edu_eldoc_registry.exceptions import (
    DocException,
)
from edu_eldoc_registry.models import (
    Certificate,
    Document,
)
from edu_eldoc_registry.permissions import (
    PERM_GROUP__CERT_REGISTRY,
    PERM_GROUP__DOC_REGISTRY,
    SUBPERM_SIGN,
    SUBPERM_VIEW,
)
from edu_eldoc_registry.ui import (
    CertificateInfoWindow,
    SignWindow,
)
from edu_eldoc_registry.utils import (
    get_download_link,
    today_date_str_for_extjs,
)


class _ObjectPack(ObjectPack):
    """
    ObjectPack с проверкой прав доступа для просмотра
    """
    need_check_permission = True

    def __init__(self):
        super().__init__()

        self.replace_action('list_window_action', _ObjectListWindowAction())
        self.replace_action('rows_action', _ObjectRowsAction())

        self.sub_permissions = {
            **self.sub_permissions,
            SUBPERM_VIEW: self.list_window_action.get_verbose_name()
        }


class _ObjectListWindowAction(ObjectListWindowAction):
    verbose_name = 'Просмотр'
    
    need_check_permission = True
    perm_code = SUBPERM_VIEW


class _ObjectRowsAction(ObjectRowsAction):
    need_check_permission = True
    perm_code = SUBPERM_VIEW


class DocumentRegistry(_ObjectPack):
    """
    Реестр электронных документов
    """
    title = 'Реестр электронных документов - Документы'
    menu_item = 'Реестр электронных документов'
    model = Document

    # Включать ли действия подписывания в паке
    # Если эти действия есть в другом паке можно 
    # отключить их чтобы избежать дублирования функционала
    use_sign_actions = True

    need_check_permission = True
    perm_code = PERM_GROUP__DOC_REGISTRY

    width = 850
    height = 600

    list_sort_order = ['-created']

    filter_engine_clz = ColumnFilterEngine

    _ff = FilterByField
    _fd = functools.partial(_ff, model)
    _fc = functools.partial(_ff, Certificate)

    columns = [
        {
            'data_index': 'id',
            'header': 'ID',
            'sortable': True,
            'hidden': True,
        },
        {
            'data_index': 'uuid',
            'header': 'UUID',
            'sortable': True,
            'hidden': True,
        },
        {
            'data_index': 'created',
            'header': 'Создан',
            'sortable': True,
            'width': 140,
            'filter': DatetimeFilterCreator(
                Document,
                'created',
            ).filter,
        },
        {
            'data_index': 'modified',
            'header': 'Изменён',
            'sortable': True,
            'hidden': True,
            'filter': DatetimeFilterCreator(
                Document,
                'modified',
            ).filter,
        },
        {
            'data_index': 'name',
            'header': 'Название',
            'sortable': True,
            'width': 80,
            'filter': _fd('name'),
        },
        {
            'data_index': 'status',
            'header': 'Статус',
            'sortable': True,
            'width': 80,
            'filter': ChoicesFilter(
                choices=DocumentStatus.get_choices(),
                parser=str,
                lookup='status'
            ),
        },
        {
            'data_index': 'download_file',
            'header': 'Файл',
            'width': 50,
        },
        {
            'data_index': 'download_sign',
            'header': 'Подпись',
            'filter': _fc(
                'subject', 
                'sign__certificate__subject__icontains'
            ),
        },
    ]

    def __init__(self):
        super().__init__()

        if self.use_sign_actions:
            self.sign_window_action = SignWindowAction()
            self.add_sign_action = AddSignAction()
            self.get_certificate_action = GetCertificateAction()

            self.actions.extend([
                self.sign_window_action,
                self.add_sign_action,
                self.get_certificate_action,
            ])

            self.sub_permissions = {
                **self.sub_permissions,
                SUBPERM_SIGN: self.sign_window_action.get_verbose_name()
            }

    def extend_menu(self, menu):
        return menu.SubMenu(
            APP_VERBOSE_NAME,
            menu.Item(
                self.menu_item,
                self.list_window_action
            ),
            icon='menu-dicts-16',
        )

    def prepare_row(self, obj, request, context):
        obj = super().prepare_row(obj, request, context)
        signs = obj.sign_set.order_by('created').select_related('certificate')
        obj.download_file = get_download_link(
            obj.file, os.path.basename(obj.file.name))

        sign_links = []
        subjects = []
        for sign in signs:
            sign_links.append(get_download_link(sign.sign_file, sign.certificate.subject))
            subjects.append(sign.certificate.subject)
        
        obj.download_sign = mark_safe("<br>".join(sign_links))
        obj.subject = mark_safe("<br>".join(subjects))

        return obj


class CertificatePack(_ObjectPack):
    """
    Информация о сертификатах
    """
    title = 'Реестр электронных документов - Сертификаты'
    menu_item = 'Информация о сертификатах'
    model = Certificate

    list_sort_order = ['-created']

    need_check_permission = True
    perm_code = PERM_GROUP__CERT_REGISTRY

    can_delete = False
    edit_window = CertificateInfoWindow

    width = 1000
    height = 800

    filter_engine_clz = ColumnFilterEngine

    _ff = FilterByField
    _fc = functools.partial(_ff, model)

    columns = [
        {
            'data_index': 'id',
            'header': 'ID',
            'sortable': True,
            'hidden': True,
        },
        {
            'data_index': 'created',
            'header': 'Создан',
            'sortable': True,
            'width': 140,
            'filter': DatetimeFilterCreator(
                Certificate,
                'created',
            ).filter,
        },
        {
            'data_index': 'modified',
            'header': 'Изменён',
            'sortable': True,
            'hidden': True,
            'filter': DatetimeFilterCreator(
                Certificate,
                'modified',
            ).filter,
        },
        {
            'data_index': 'name',
            'header': 'Название',
            'sortable': True,
            'filter': _fc('name'),
        },
        {
            'data_index': 'subject',
            'header': 'Владелец',
            'sortable': True,
            'filter': _fc('subject'),
        },
        {
            'data_index': 'issuer',
            'header': 'Издатель',
            'sortable': True,
            'filter': _fc('issuer'),
        },
        {
            'data_index': 'date_from',
            'header': 'Действителен с',
            'sortable': True,
            'filter': _fc(
                'date_from', 
                'date_from__gte',
            ),
        },
        {
            'data_index': 'date_to',
            'header': 'Действителен до',
            'sortable': True,
            'filter': _fc(
                'date_to', 
                'date_to__lte',
            ),
        },
        {
            'data_index': 'serial',
            'header': 'Серийный номер',
            'sortable': True,
            'filter': _fc('serial'),
        },
    ]

    def __init__(self):
        super().__init__()

        self.get_signed_docs_action = GetSignedDocsAction()

        self.actions.extend([
            self.get_signed_docs_action
        ])

    def configure_grid(self, grid):
        super().configure_grid(grid)
        grid.url_new = None
        grid.url_delete = None
        grid.top_bar.button_edit.text = 'Просмотр'
        grid.top_bar.button_edit.icon_cls = Icons.MAGNIFIER
        context_menu_row = grid.context_menu_row
        context_menu_row.menuitem_edit.text = "Просмотр"
        context_menu_row.menuitem_edit.icon_cls = Icons.MAGNIFIER

    def get_edit_window_params(self, params, request, context):
        params = super().get_edit_window_params(params, request, context)
        params.update({
            'get_signed_docs_url': self.get_signed_docs_action.get_absolute_url()
        })

        return params

    def extend_menu(self, menu):
        return menu.SubMenu(
            APP_VERBOSE_NAME,
            menu.Item(
                self.menu_item,
                self.list_window_action
            ),
            icon='menu-dicts-16',
        )


class SignWindowAction(BaseWindowAction):
    """
    Экшн окна подписывания
    """
    verbose_name = 'Подписание документа'

    need_check_permission = True
    perm_code = SUBPERM_SIGN

    def create_window(self):
        self.win = SignWindow()
    
    def context_declaration(self):
        context = super().context_declaration()

        context.update({
            # ID документов для подписывания
            'doc_ids': {'type': 'int_list'},
            # Признак прикреплённой подписи
            'attached': {'type': 'boolean'},
        })

        return context
    
    @property
    def add_sign_action(self):
        """
        Экшн подписывания

        Можно переопределить если отличается в паке куда добавляется экшн
        """
        return self.parent.add_sign_action
    
    @property
    def get_certificate_action(self):
        """
        Экшн получения сертификата

        Можно переопределить если отличается в паке куда добавляется экшн
        """
        return self.parent.get_certificate_action

    def set_window_params(self):
        super().set_window_params()
        docs = Document.objects.filter(pk__in=self.context.doc_ids)
        if not docs:
            raise ApplicationLogicException(self.parent.MSG_DOESNOTEXISTS)

        if docs.exclude(status=DocumentStatus.READY.id).exists():
            raise ApplicationLogicException(
                'Подписать можно только документы в статусе "Готов к подписанию"')

        self.win_params['attached'] = self.context.attached
        self.win_params['title'] = self.verbose_name
        self.win_params['documents'] = docs
        self.win_params['add_sign_url'] = (
            self.add_sign_action.get_absolute_url())
        self.win_params['get_certificate_url'] = (
            self.get_certificate_action.get_absolute_url())


class GetCertificateAction(BaseAction):
    """
    Экшн получения сертификата

    Если сертификат не найден будет создан новый
    """
    verbose_name = 'Получение идентификатора сертификата'

    need_check_permission = True
    perm_code = SUBPERM_SIGN

    def context_declaration(self):
        context = super().context_declaration()

        context.update({
            # Название сертификата
            'name': {'type': 'str'},
            # Серийный номер сертификата
            'serial': {'type': 'str'},
            # Владелец сертификата
            'subject': {'type': 'str'},
            # Издатель сертификата
            'issuer': {'type': 'str'},
            # Сертификат действителен с
            'date_from': {'type': 'date'},
            # Сертификат действителен по
            'date_to': {'type': 'date'},
        })

        return context
    
    def run(self, request, context):
        cert, created = Certificate.objects.get_or_create(
            serial=context.serial,
            defaults={
                'name': context.name,
                'subject': context.subject,
                'issuer': context.issuer,
                'date_from': context.date_from,
                'date_to': context.date_to,
            }
        )

        return PreJsonResult({'id': cert.id, 'created': created})


class AddSignAction(BaseAction):
    """
    Экшн добавления подписи к документам
    """
    verbose_name = 'Добавление подписи'

    need_check_permission = True
    perm_code = SUBPERM_SIGN
    # Расширение файла с подписью
    sign_extension = EXT_SIG

    def context_declaration(self):
        context = super().context_declaration()

        context.update({
            # ID сертификата
            'cert_id': {'type': 'int'},
            # Признак прикреплённой подписи
            'attached': {'type': 'boolean'},
            # Данные подписи в формате
            # [{"id": <ID документа>, "sign": <подпись в формате base64>}, ...]
            'data': {'type': 'json'},
        })

        return context
    
    def add_sign(self, document, certificate, attached, sign_data):
        """
        Добавление подписи к документу
        """
        sign_document(
            document,
            sign_data,
            attached,
            certificate,
            sign_extension=self.sign_extension,
            last_sign=self.get_last_sign(),
        )
    
    def get_certificate(self, id_):
        """
        Получить сертификат
        """
        return Certificate.objects.get(pk=id_)
    
    def get_document(self, id_):
        """
        Получить документ
        """
        return Document.objects.get(pk=id_)
    
    def get_last_sign(self):
        """
        Нужно ли менять статус документа

        По умолчанию меняет всегда, но можно переопределить 
        если нужно добавить несколько подписей к одному документу
        """
        return True

    def run(self, request, context):
        cert = self.get_certificate(context.cert_id)
        for sign_data in context.data:
            doc = self.get_document(sign_data['id'])
            try:
                self.add_sign(doc, cert, context.attached, sign_data['sign'])
            except DocException as e:
                raise ApplicationLogicException(str(e))

        return OperationResult()


class GetSignedDocsAction(BaseAction):
    """
    Экшн получения документов подписанных сертификатом
    """
    verbose_name = 'Получение списка документов подписанных сертификатом'
    need_check_permission = True
    perm_code = SUBPERM_VIEW

    def set_query(self):
        """
        Запрос на получение документов
        """
        cert_id = getattr(self.context, self.parent.id_param_name)
        self.query = Document.objects.filter(sign__certificate_id=cert_id)

    def get_total_count(self):
        """
        Возвращает общее кол-во объектов
        """
        return self.query.count()

    def get_rows(self):
        """
        Метод производит преобразование QuerySet в список.
        При этом объекты сериализуются в словари
        """
        res = []
        for obj in self.query:
            prep_obj = self.prepare_object(obj)
            if prep_obj:
                res.append(prep_obj)
        return res

    def prepare_object(self, obj):
        """
        Возвращает словарь, для составления результирующего списка
        """
        cert_id = getattr(self.context, self.parent.id_param_name)
        data = {
            'id': obj.id,
            'name': obj.name,
            'created': obj.created.strftime('%d.%m.%Y %H:%M:%S')
        }

        sign = obj.sign_set.filter(certificate_id=cert_id).order_by('created').last()
        data['download_file'] = get_download_link(obj.file)
        if sign:
            data['download_sign'] = get_download_link(sign.sign_file)

        return data

    def run(self, request, context):
        new_self = copy.copy(self)
        new_self.request = request
        new_self.context = context

        new_self.set_query()
        total_count = new_self.get_total_count()
        rows = new_self.get_rows()
        result = PreJsonResult({
            'rows': rows,
            'total': total_count
        })

        return result
