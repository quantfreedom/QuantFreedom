class ApexproError(Exception):
    """Base error class for all exceptions raised in this library.
    Will never be raised naked; more specific subclasses of this exception will
    be raised when appropriate."""


class ApexproApiError(ApexproError):

    def __init__(self, response):
        self.status_code = response.status_code
        try:
            self.msg = response.json()
        except ValueError:
            self.msg = response.text
        self.response = response
        self.request = getattr(response, 'request', None)

    def __str__(self):
        return self.__repr__()

    def __repr__(self):
        return 'ApexproApiError(status_code={}, response={})'.format(
            self.status_code,
            self.msg,
        )


class TransactionReverted(ApexproError):

    def __init__(self, tx_receipt):
        self.tx_receipt = tx_receipt



