from .bases import Pys
from .utils import to_str

class PysException(Pys):

    def __init__(self, exception, context, position):
        self.exception = exception
        self.context = context
        self.position = position

    def __str__(self):
        return str(self.exception)

    def __repr__(self):
        return '<Exception of {!r}>'.format(self.exception)

class PysShouldReturn(Pys, BaseException):

    def __init__(self, result):
        super().__init__()
        self.result = result

    def __str__(self):
        if self.result.error is None:
            return '<signal>'

        exception = self.result.error.exception
        message = to_str(exception)

        return (
            exception.__name__
                if isinstance(exception, type) and issubclass(exception, BaseException) else
            type(exception).__name__
        ) + (': {}'.format(message) if message else '')