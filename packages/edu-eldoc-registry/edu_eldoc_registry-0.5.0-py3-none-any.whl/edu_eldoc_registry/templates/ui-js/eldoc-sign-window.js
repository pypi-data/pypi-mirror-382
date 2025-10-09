{% include 'ui-js/eldoc-sign-functions.js' %}

let certField = Ext.getCmp('{{ component.certificate.client_id }}');

let certInfoNameField = Ext.getCmp('{{ component.cert_info_name.client_id }}');
let certInfoSerialField = Ext.getCmp('{{ component.cert_info_serial.client_id }}');
let certInfoSubjectField = Ext.getCmp('{{ component.cert_info_subject.client_id }}');
let certInfoIssuerField = Ext.getCmp('{{ component.cert_info_issuer.client_id }}');
let certInfoDateFromField = Ext.getCmp('{{ component.cert_info_date_from.client_id }}');
let certInfoDateToField = Ext.getCmp('{{ component.cert_info_date_to.client_id }}');

let docGrid = Ext.getCmp('{{ component.doc_grid.client_id }}');
let signWinMask = new Ext.LoadMask(win.getEl(), {msg: 'Загрузка и подписывание файлов'});
let attached = {% if component.attached %}true{% else %}false{% endif %};

/**
 * Показать ошибку и закрыть окно
 * 
 * @param {string} text Текст ошибки
 */
function showError(text) {
    // Удаляет код ошибки из сообщения.
    let message = text.replace(/( [[A-Za-z0-9]*])/g, "");
    switch (message) {
        case "Плагин недоступен":
            message = "У Вас не установлен или не настроен плагин для работы с ЭЦП. Выполнить подписание документа невозможно! Для подписания документа установите и настройте плагин!"
            break;
        case "Истекло время ожидания загрузки плагина":
            message = "У Вас отсутствует или не настроена ЭЦП. Выполнить подписание документа невозможно! Для подписания документа настройте ЭЦП!";
            break;
    }

    Ext.Msg.show({
        modal:true,
        title:'Ошибка',
        msg: message,
        buttons:Ext.Msg.OK,
        icon: Ext.Msg.WARNING,
    });
    win.close();
}

/**
 * Действие при выборе сертификата
 * 
 * @param {Ext.form.ComboBox} el 
 */
function onSelectCert(el) {
    cryptopro.certificateInfo(el.getValue()).then(info => {
        certInfoNameField.setValue(info.Name);
        certInfoSerialField.setValue(info.SerialNumber);
        certInfoSubjectField.setValue(info.Subject.CN);
        certInfoIssuerField.setValue(info.Issuer.CN);
        certInfoDateFromField.setValue(info.ValidFromDate);
        certInfoDateToField.setValue(info.ValidToDate);
    });
}

certField.on('select', onSelectCert);

// Получаем сертификаты пользователя
loadCerts(
    data => {
        certField.getStore().loadData(data);
        if (data.length > 0) {
            let certID = data[0][0];
            certField.setValue(certID);
            onSelectCert(certField);
        }
    },
    function(error) {
        return showError(error.message);
    }
);

/**
 * Подписать документ с переданным сертификатом
 * 
 * @param {number} certId ID сертификата в системе
 */
function signDocument(certId) {
    let store = docGrid.getStore();
    let thumbprint = certField.getValue();
    // Сначала собираем все задачи на подпись для каждого файла
    let tasks = store.data.items.map(el => {
        return signRecord(el.data.id, el.data.url, thumbprint);
    });

    // Подписываем все файлы и передаём подписи по указанному URL
    Promise.all(tasks).then(
        signData => {
            if (signData.includes(undefined)) {
                showError('Один из документов не подписан');
                return
            }
            Ext.Ajax.request({
                url: "{{ component.add_sign_url }}",
                params: {
                    'cert_id': certId,
                    'attached': attached,
                    'data': Ext.util.JSON.encode(
                        signData.map(([id, sign]) => {
                            return {
                                'id': id,
                                'sign': sign
                            }
                        })
                    )
                },
                success: function (response) {
                    signWinMask.hide();
                    let obj = Ext.util.JSON.decode(response.responseText);
                    if (obj.success) {
                        win.close();
                    } else {
                        showError(obj.message);
                    }
                },
                failure: function (response, opts) {
                    win.close();
                    uiAjaxFailMessage();
                }
            });
        },
        rejectReason => {
            showError(rejectReason);
        }
    ).catch(error => {
        showError(`Ошибка при подписывании: ${error}`);
    });
}

/**
 * Подписать документы
 */
function submit() {
    signWinMask.show();
    
    if (
        !certField.getValue() &&
        !certInfoNameField.getValue() &&
        !certInfoSerialField.getValue() &&
        !certInfoSubjectField.getValue() &&
        !certInfoIssuerField.getValue() &&
        !certInfoDateFromField.getValue() &&
        !certInfoDateToField.getValue()
    ) {
        Ext.Msg.show({
            modal:true,
            title:'Ошибка',
            msg: 'Сертификат не выбран',
            buttons:Ext.Msg.OK,
            icon: Ext.Msg.WARNING,
        });
        signWinMask.hide();
        return
    }

    Ext.Ajax.request({
        url: "{{ component.get_certificate_url }}",
        params: {
            'name': certInfoNameField.getValue(),
            'serial': certInfoSerialField.getValue(),
            'subject': certInfoSubjectField.getValue(),
            'issuer': certInfoIssuerField.getValue(),
            'date_from': certInfoDateFromField.getValue(),
            'date_to': certInfoDateToField.getValue(),
        },
        success: function (response) {
            let obj = Ext.util.JSON.decode(response.responseText);
            if (obj.message) {
                showError(obj.message);
                return
            }
            signDocument(obj.id);
        },
        failure: function (response, opts) {
            win.close();
            uiAjaxFailMessage();
        }
    });
}
