import base64
import datetime
import os
import shutil
import tempfile
import uuid
from pathlib import (
    Path,
)

from django.core.files.base import (
    ContentFile,
)
from django.test import (
    TestCase,
    override_settings,
)

from edu_eldoc_registry.api.common import (
    mark_ready,
    mark_rejected,
    mark_signed,
    sign_document,
)
from edu_eldoc_registry.constants import (
    EXT_SGN,
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


TMP_MEDIA_ROOT = tempfile.mkdtemp()
SIGN_DOCUMENT_STORE_PATH = 'test_sign'

def _generate_file_data():
    """
    Генерация данных файла
    """
    data = uuid.uuid1().hex
    return bytes(data, encoding='utf-8'), data


def _generate_base64_data():
    """
    Генерация данных файла в формате base64
    """
    data, content = _generate_file_data()
    return base64.b64encode(data), content


@override_settings(MEDIA_ROOT=TMP_MEDIA_ROOT, 
                   SIGN_DOCUMENT_STORE_PATH=SIGN_DOCUMENT_STORE_PATH)
class DocumentTestCase(TestCase):
    databases = '__all__'

    def setUp(self) -> None:
        super().setUp()
        
        self.cert_0 = Certificate.objects.create(
            serial='7c000000000000000000000000000000000000',
            name='Test Certificate 0',
            subject='Test Subject 0',
            issuer='Test Issuer 0',
            date_from=datetime.date.today(),
            date_to=datetime.date(9999, 12, 31),
        )

        self.cert_1 = Certificate.objects.create(
            serial='7c111111111111111111111111111111111111',
            name='Test Certificate 1',
            subject='Test Subject 1',
            issuer='Test Issuer 1',
            date_from=datetime.date.today(),
            date_to=datetime.date(9999, 12, 31),
        )

    def tearDown(self):
        super().tearDown()
        if os.path.isdir(TMP_MEDIA_ROOT):
            shutil.rmtree(TMP_MEDIA_ROOT)

    def _create_document(self, **kwargs):
        name = f'{uuid.uuid1().hex}.txt'

        data, content = _generate_file_data()
        doc = Document.objects.create(
            name=name,
            file=ContentFile(data, name),
            **kwargs
        )

        return doc, content

    def _assert_file_content(self, file, expected_content):
        with file.open() as f:
            data = f.readline()
            self.assertEqual(data.decode('utf-8'), expected_content)

    def test_mark_ready(self):
        """
        Проверяем смену статуса документа на "Готов к подписанию"
        """
        doc, _ = self._create_document(status=DocumentStatus.NEW.id)
        self.assertEqual(doc.status, DocumentStatus.NEW.id)
        # Помечаем документ как "Готовый к подписанию" и проверяем что статус сменился
        mark_ready(doc)
        self.assertEqual(doc.status, DocumentStatus.READY.id)

        # Второй раз статус сменить нельзя так как изначальный статус не "Новый"
        with self.assertRaises(DocException):
            mark_ready(doc)

    def test_signing_doc(self):
        """
        Проверяем добавление подписи к документу
        """
        doc, _ = self._create_document(status=DocumentStatus.NEW.id)
        sign, sig_content = _generate_base64_data()
        other_sign, other_content = _generate_base64_data()

        # Подписать новый документ нельзя, сначала нужно пометить 
        # его как "Готовый к подписанию"
        with self.assertRaises(SignException):
            sign_document(doc, sign, True, self.cert_0, last_sign=False)
        self.assertFalse(Sign.objects.filter(document=doc).exists())

        mark_ready(doc)
        sign_0 = sign_document(doc, sign, True, self.cert_0, last_sign=False)
        # После добавления подписи проверяем что подпись добавлена, 
        # расширение файла по умолчанию и файл идентичен ожидаемому файлу подписи 
        self.assertEqual(Sign.objects.filter(document=doc).count(), 1)
        self._assert_file_content(sign_0.sign_file, sig_content)
        self.assertEqual(Path(sign_0.sign_file.path).suffix, f'.{EXT_SIG}')
        
        # Проверим добавление нескольких подписей
        with self.assertRaises(SignException):
            # Нельзя подписать документ одним сертификатом дважды 
            sign_document(doc, other_sign, True, self.cert_0, last_sign=False)
        sign_1 = sign_document(doc, other_sign, True, self.cert_1, last_sign=False)
        self.assertEqual(Sign.objects.filter(document=doc).count(), 2)
        self._assert_file_content(sign_1.sign_file, other_content)
        self.assertEqual(Path(sign_1.sign_file.path).suffix, f'.{EXT_SIG}')

        # Проверяем что первая подпись всё ещё на месте
        self._assert_file_content(sign_0.sign_file, sig_content)

    def test_mark_signed(self):
        """
        Проверяем перевод документа в статус "Подписано"
        """
        doc, _ = self._create_document(status=DocumentStatus.NEW.id)
        sign, _ = _generate_base64_data()

        # Можно пометить подписанным только если 
        # статус документа = "Готов к подписанию"
        with self.assertRaises(DocException):
            mark_signed(doc)
        
        mark_ready(doc)
        # У документа нет подписей
        with self.assertRaises(DocException):
            mark_signed(doc)
        
        sign_document(doc, sign, True, self.cert_0, last_sign=False)
        mark_signed(doc)
        self.assertEqual(doc.status, DocumentStatus.SIGNED.id)

    def test_signing_doc_with_status_change(self):
        """
        Проверяем добавление подписи к документу с последующей сменой статуса
        """
        doc, _ = self._create_document()
        sign, sig_content = _generate_base64_data()

        sign = sign_document(
            doc, sign, True, self.cert_0, sign_extension=EXT_SGN, last_sign=True)

        # После добавления подписи проверяем что подпись добавлена, 
        # расширение файла указанное нами и файл идентичен ожидаемому файлу подписи 
        self.assertEqual(Sign.objects.filter(document=doc).count(), 1)
        self._assert_file_content(sign.sign_file, sig_content)
        self.assertEqual(Path(sign.sign_file.path).suffix, f'.{EXT_SGN}')
        self.assertEqual(doc.status, DocumentStatus.SIGNED.id)

    def test_mark_rejected(self):
        """
        Проверяем перевод документа в статус "Отклонён"
        """
        doc_0, _ = self._create_document()
        doc_1, _ = self._create_document()

        sign, _ = _generate_base64_data()

        # Один из документов уже подписан
        sign_document(doc_0, sign, True, self.cert_0, last_sign=False)

        # Подписанный документ нельзя отклонить
        with self.assertRaises(DocException):
            mark_rejected(doc_0)
        self.assertEqual(doc_0.status, DocumentStatus.READY.id)

        # Отклоняем документ и проверяем смену статуса
        mark_rejected(doc_1)
        self.assertEqual(doc_1.status, DocumentStatus.REJECTED.id)

        # Нельзя отклонить документ во второй раз
        with self.assertRaises(DocException):
            mark_rejected(doc_1)
        
        # Если передан raise_rejected=False функция не бросит исключения
        mark_rejected(doc_1, raise_rejected=False)
