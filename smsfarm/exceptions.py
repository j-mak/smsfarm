class SOAPError(Exception):
    def __init__(self, exc):
        self.code = exc.code
        self.message = exc.message
        self.detail = exc.detail
        self.subcodes = exc.subcodes
        self.actor = exc.actor
        self.args = exc.args


class NotSpecifiedError(Exception):
    pass
