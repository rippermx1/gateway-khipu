
class KhipuGetBanksException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


class PaymentException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message
