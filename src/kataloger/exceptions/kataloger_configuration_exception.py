from kataloger.exceptions.kataloger_exception import KatalogerException


class KatalogerConfigurationException(KatalogerException):
    def __init__(self, message: str):
        super().__init__(message)
