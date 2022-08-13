class SendMessageError(Exception):
    """Исключение невозможности отправки сообщения"""
    pass


class BadStatuscodeError(Exception):
    """Исключение при статус коде отличном от 200"""
    pass
