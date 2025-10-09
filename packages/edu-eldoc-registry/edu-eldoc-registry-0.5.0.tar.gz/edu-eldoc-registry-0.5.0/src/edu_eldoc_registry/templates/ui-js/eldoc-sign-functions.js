let cryptopro = new window.RusCryptoJS.CryptoPro;

/**
 * Загружает доступные для подписи сертификаты
 * 
 * @param {funciton} success Действие по завершению загрузки сертификатов
 * @param {funciton} onerror Действие по ошибке при загрузке сертификатов
 */
function loadCerts(success, onerror) {
    cryptopro.init().then(
        () => cryptopro.listCertificates()
    ).then(
        certs => {
            let data = certs.filter(
                cert => cert.validTo >= Date.now()
            ).map(cert => {
                let name = `${cert.name} (${cert.subject.CN}, сертификат действителен по ${cert.validTo.toLocaleDateString()})`;
                return [cert.id, name]
            });

            success(data);
            
        }
    ).catch(
        onerror
    )
}

/**
 * Загружает файл (в формате base64) используя ссылку из записи, 
 * подписывает файл и верифицирует подпись
 * 
 * @param {number} docID ID Документа
 * @param {string} docURL URL Документа
 * @param {string} thumbprint Сертификат
 * @returns {Promise} Promise пары [ID Документа, подпись в base64]
 */
async function signRecord(docID, docURL, thumbprint) {
    // Сначала скачиваем файл с сервера
    const response = await fetch(docURL);

    if (!response.ok) {
        throw new Error(`Ошибка при загрузке файла: ${response.statusText}`);
    }
    const blob = await response.blob();
    return await new Promise((resolve, reject) => {
        const reader = new FileReader();

        // По завершению загрузки файла подписываем документ
        reader.onloadend = function () {
            // Отбрасываем часть, так как нам нужен чистый base64
            let data = reader.result.split(',')[1];
            cryptopro.init().then(() => {
                // Подписание
                return cryptopro.signData(data, thumbprint, { attached });
            }).then(sign => {
                // Верификация созданной подписи
                cryptopro.verifySign(data, sign, { attached }).then(verified => {
                    if (verified) {
                        // Успешное подписание, возвращаем пару 
                        // [ID документа, подпись в формате base64]
                        resolve([docID, sign]);
                    } else {
                        reject('Подпись не верифицирована, отмена операции');
                    }
                }).catch(e => {
                    reject('Ошибка при верификации подписи');
                });
            }, rejectReason => {
                reject(rejectReason);
            }).catch(e => {
                reject(e);
            });
        };
        reader.onerror = reject;
        // Файл нам нужен в формате base64
        reader.readAsDataURL(blob);
    });
}
