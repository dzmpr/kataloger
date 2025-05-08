from kataloger.exceptions.kataloger_exception import KatalogerError


class KatalogerParseError(KatalogerError):
    def __init__(self, message: str):
        super().__init__(message)
