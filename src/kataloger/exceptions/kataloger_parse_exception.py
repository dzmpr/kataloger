from kataloger.exceptions.kataloger_exception import KatalogerException


class KatalogerParseException(KatalogerException):
    def __init__(self, message: str):
        super().__init__(message)
