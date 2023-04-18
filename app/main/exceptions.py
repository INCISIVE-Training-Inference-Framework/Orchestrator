class UserError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class InternalError(Exception):
    def __init__(self, message: str, exception: Exception):
        super().__init__(message)
        self.message = message
        self.exception = exception

    def get_message(self):
        return self.message

    def get_exception(self):
        if self.exception:
            return self.exception
        else:
            return self
