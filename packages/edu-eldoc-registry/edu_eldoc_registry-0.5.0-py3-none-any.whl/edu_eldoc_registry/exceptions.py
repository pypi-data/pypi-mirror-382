class DocException(Exception):
    """
    Ошибка при работе с электронным документом
    """


class SignException(DocException):
    """
    Ошибка при создании подписи для документа
    """
