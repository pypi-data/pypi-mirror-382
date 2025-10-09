from __future__ import (
    annotations,
)

from django.utils.safestring import (
    mark_safe,
)

from m3_ext.ui.all_components import (
    ExtComboBox,
)
from m3_ext.ui.base import (
    ExtUIComponent,
)
from m3_ext.ui.containers.containers import (
    ExtContainer,
)
from m3_ext.ui.containers.forms import (
    ExtFieldSet,
    ExtPanel,
)
from m3_ext.ui.containers.grids import (
    ExtGrid,
    ExtGridColumn,
)
from m3_ext.ui.controls.buttons import (
    ExtButton,
)
from m3_ext.ui.fields.base import (
    BaseExtTriggerField,
)
from m3_ext.ui.fields.simple import (
    ExtDateField,
    ExtStringField,
)
from m3_ext.ui.misc import (
    ExtDataStore,
)
from m3_ext.ui.misc.store import (
    ExtJsonStore,
)
from objectpack.ui import (
    BaseEditWindow,
    BaseWindow,
)


def _wrap_to_form_container(el: ExtUIComponent) -> ExtContainer:
    """
    Обернуть элемент в контейнер с layout = form

    :param el: Элемент который нужно обернуть
    """
    item_container = ExtContainer(
        layout='form',
        flex=1,
        label_width='15px'
    )
    item_container.items.append(el)
    return item_container


def get_cert_fields(bind_to: ExtUIComponent | None = None) -> ExtFieldSet:
    """
    Филдсет для информации о сертификате

    :param bind_to: Привязать созданные поля к компоненту
    """
    cert_info_name = ExtStringField(
        name='name',
        label='Название',
        anchor='100%',
        read_only=True
    )
    cert_info_serial = ExtStringField(
        name='serial',
        label='Серийный номер',
        anchor='100%',
        read_only=True
    )
    cert_info_subject = ExtStringField(
        name='subject',
        label='Владелец',
        anchor='100%',
        read_only=True
    )
    cert_info_issuer = ExtStringField(
        name='issuer',
        label='Издатель',
        anchor='100%',
        read_only=True
    )
    cert_info_date_from = ExtDateField(
        name='date_from',
        label='Действителен с',
        read_only=True
    )
    cert_info_date_to = ExtDateField(
        name='date_to',
        label='Действителен по',
        read_only=True
    )

    info_container = ExtFieldSet(
        title='Информация о сертификате',
        layout='form'
    )

    info_panel_date_row = ExtContainer(
        layout='hbox'
    )

    info_panel_date_row.items.extend([
        _wrap_to_form_container(cert_info_date_from),
        _wrap_to_form_container(cert_info_date_to),
    ])

    info_container.items.extend([
        cert_info_name,
        cert_info_serial,
        cert_info_subject,
        cert_info_issuer,
        info_panel_date_row
    ])

    if bind_to:
        bind_to.cert_info_name = cert_info_name
        bind_to.cert_info_serial = cert_info_serial
        bind_to.cert_info_subject = cert_info_subject
        bind_to.cert_info_issuer = cert_info_issuer
        bind_to.cert_info_date_from = cert_info_date_from
        bind_to.cert_info_date_to = cert_info_date_to

    return info_container


class CertificateInfoWindow(BaseEditWindow):
    """
    Просмотр информации о сертификате
    """
    def _init_components(self) -> None:
        super()._init_components()
        self.info_container = get_cert_fields(self)

        self.doc_grid = ExtGrid(
            load_mask=True
        )

        self.doc_grid.columns.extend((
            ExtGridColumn(header='ID', data_index='id', hidden=True),
            ExtGridColumn(header='Название файла', data_index='name'),
            ExtGridColumn(header='Добавлен', data_index='created'),
            ExtGridColumn(header='Файл', data_index='download_file'),
            ExtGridColumn(header='Подпись', data_index='download_sign'),
        ))

        self.documents_panel = ExtPanel(
            layout='fit',
            body_cls='x-window-mc',
            region='south',
            padding='5px',
            title='Подписанные сертификатом документы',
            header=True,
            height=200
        )
    
    def _do_layout(self) -> None:
        self.layout = 'border'
        self.form.region = 'center'
        self.form.items.append(self.info_container)
        self.documents_panel.items.append(self.doc_grid)
        self.items.append(self.documents_panel)

    def set_params(self, params: dict) -> None:
        super().set_params(params)

        self.title = 'Информация о сертификате'
        self.width = 520
        self.height = 420

        self.doc_grid.store = ExtJsonStore(
            auto_load=True, root='rows', 
            id_property='id', url=params['get_signed_docs_url'])


class SignWindow(BaseWindow):
    """
    Окно проставления подписи к документам
    """
    def _init_components(self) -> None:
        self.certificate = ExtComboBox(
            allow_blank=False,
            name='mode',
            label='Сертификат',
            anchor='100%',
            display_field='name',
            value_field='id',
            store=ExtDataStore(data=[]),
            trigger_action=BaseExtTriggerField.ALL,
            editable=False,
            flex=1
        )

        self.info_container = get_cert_fields(self)

        self.doc_grid = ExtGrid()

        self.doc_grid.columns.extend((
            ExtGridColumn(header='ID', data_index='id', hidden=True),
            ExtGridColumn(header='Название файла', data_index='name'),
            ExtGridColumn(header='Добавлен', data_index='created'),
            ExtGridColumn(header='Ссылка', data_index='link'),
            ExtGridColumn(
                header='URL', data_index='url', hidden=True, hideable=False),
        ))

        self.select_panel = ExtPanel(
            layout='form',
            body_cls='x-window-mc',
            region='center',
            padding='5px'
        )

        self.documents_panel = ExtPanel(
            layout='fit',
            body_cls='x-window-mc',
            region='south',
            padding='5px',
            title='Документы на подписание',
            header=True,
            height=200
        )

        self.submit_btn = ExtButton(
            text='Подписать', handler="submit")

        self.cancel_btn = ExtButton(
            text='Отмена', handler="closeWindow")

    def _wrap_to_form_container(self, el: ExtUIComponent) -> ExtContainer:
        """
        Обернуть элемент в контейнер с layout = form
        """
        item_container = ExtContainer(
            layout='form',
            flex=1,
            label_width='15px'
        )

        item_container.items.append(el)

        return item_container

    def _do_layout(self) -> None:
        self.layout = 'border'

        self.select_panel.items.extend([
            self.certificate,
            self.info_container,
        ])

        self.documents_panel.items.extend([
            self.doc_grid
        ])

        self.items.extend([
            self.select_panel,
            self.documents_panel,
        ])

        self.buttons.extend([
            self.submit_btn,
            self.cancel_btn,
        ])

    def set_params(self, params: dict) -> None:
        """
        Параметры:

        Заголовок окна (по умолчанию Подписание документов)
        title: NotRequired[str]

        Ширина окна (по умолчанию 640)
        width: NotRequired[int]

        Высота (по умолчанию 480)
        height: NotRequired[int]

        URL экшна подписания 
        add_sign_url: str

        URL экшна получения сертификата
        get_certificate_url: str

        Признак прикреплённой подписи (по умолчанию False)
        attached: NotRequired[bool]

        Документы для подписи
        documents: Iterable[Document]
        """
        super().set_params(params)
        self.template_globals = 'ui-js/eldoc-sign-window.js'
        self.title = params.get('title', 'Подписание документов')
        self.width = params.get('width', 640)
        self.height = params.get('height', 480)
        self.add_sign_url = params['add_sign_url']
        self.get_certificate_url = params['get_certificate_url']
        self.attached = params.get('attached', False)

        doc_data = []
        for doc in params['documents']:
            doc_data.append([
                doc.id,
                doc.name,
                doc.created.strftime('%d.%m.%Y %H:%M:%S'),
                mark_safe(
                    f'<a href="{doc.file.url}" target="_blank">Скачать</a>'),
                doc.file.url
            ])
        self.doc_store = ExtDataStore(data=doc_data)
        self.doc_grid.store = self.doc_store
