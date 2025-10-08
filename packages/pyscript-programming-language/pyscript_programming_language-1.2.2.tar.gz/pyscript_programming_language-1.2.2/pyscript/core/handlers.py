from .cache import hook
from .exceptions import PysException, PysShouldReturn
from .objects import PysChainFunction, PysFunction
from .utils import is_object_of

from contextlib import contextmanager
from types import MethodType

@contextmanager
def handle_exception(result, context, position):
    try:
        yield
    except PysShouldReturn as e:
        result.register(e.result)
    except BaseException as e:
        result.failure(PysException(e, context, position))

def handle_call(object, context, position, flags):
    if isinstance(object, PysFunction):
        object.__code__.call_context = context
        object.__code__.position = position
        object.__code__.flags = flags

    elif isinstance(object, PysChainFunction):
        object.__code__.context = context
        object.__code__.position = position
        object.__code__.flags = flags

    elif isinstance(object, MethodType) and isinstance(object.__func__, PysFunction):
        object.__func__.__code__.call_context = context
        object.__func__.__code__.position = position
        object.__func__.__code__.flags = flags

    elif isinstance(object, type):

        for call in ('__init__', '__new__'):
            fn = getattr(object, call, None)

            if isinstance(fn, PysFunction):
                fn.__code__.call_context = context
                fn.__code__.position = position
                fn.__code__.flags = flags

def handle_execute(result):
    try:

        if result.error:
            if is_object_of(result.error.exception, SystemExit):
                return result.error.exception.code
            if hook.exception is not None:
                hook.exception(result.error)
            return 1

        elif len(result.result) == 1 and hook.display is not None:
            hook.display(result.result[0])

    except:
        return 1

    return 0