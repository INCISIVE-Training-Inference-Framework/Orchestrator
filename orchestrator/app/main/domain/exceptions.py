class UserError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


class InternalError(Exception):
    def __init__(self, internal_message, public_message):
        self.internal_message = internal_message
        self.public_message = public_message
        super().__init__(self.public_message)
