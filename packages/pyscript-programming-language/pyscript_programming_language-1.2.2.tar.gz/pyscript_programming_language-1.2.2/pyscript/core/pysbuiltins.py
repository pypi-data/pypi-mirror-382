from .objects import PysModule, PysChainFunction
from .utils import is_object_of as isobjectof

from importlib import import_module as pyimport

class _Printer:

    def __init__(self, name, content):
        self.name = name
        self.content = content

    def __repr__(self):
        return 'Type {}() to see the full information text.'.format(self.name)

    def __call__(self):
        print(self.content)

license = _Printer(
    'license',

    "MIT License - PyScript created by AzzamMuhyala.\n"
    "This language was written as a project and learning how language is works.\n"
    "For more information see on https://github.com/azzammuhyala/pyscript."
)

def require(chain, name):
    from .buffer import PysFileBuffer
    from .cache import loading_modules, library, modules
    from .constants import LIBRARY_PATH
    from .runner import pys_runner
    from .utils import build_symbol_table, to_str, normalize_path

    import os

    name = to_str(name)
    dirname = os.path.dirname(chain.__code__.context.file.name) or os.getcwd()

    if name == '_pyscript':
        from .. import core
        return core

    elif name == 'builtins':
        return pys_builtins

    elif name in library:
        path = os.path.join(LIBRARY_PATH, name)
        if not os.path.isdir(path):
            path += '.pys'
        if not os.path.exists(path):
            path = normalize_path(dirname, name, absolute=False)

    else:
        path = normalize_path(dirname, name, absolute=False)

    filename = os.path.basename(path)

    if os.path.isdir(path):
        path = os.path.join(path, '__init__.pys')

    if path in loading_modules:
        raise ImportError(
            "cannot import module name {!r} from partially initialized module {!r}, mostly during circular import"
            .format(filename, chain.__code__.context.file.name)
        )

    loading_modules.add(path)

    try:

        try:
            with open(path, 'r') as file:
                file = PysFileBuffer(file.read(), path)
        except FileNotFoundError:
            raise ModuleNotFoundError("No module named {!r}".format(filename))
        except BaseException as e:
            raise ImportError("Cannot import module named {!r}: {}".format(filename, e))

        package = modules.get(path, None)

        if package is None:
            symtab = build_symbol_table(file)
            modules[path] = package = symtab.module

            result = pys_runner(
                file=file,
                mode='exec',
                flags=chain.__code__.flags,
                symbol_table=symtab,
                context_parent=chain.__code__.context,
                context_parent_entry_position=chain.__code__.position
            )

            if result.error:
                from .exceptions import PysShouldReturn
                from .results import PysRunTimeResult

                raise PysShouldReturn(PysRunTimeResult().failure(result.error))

        return package

    finally:
        if path in loading_modules:
            loading_modules.remove(path)

def globals(chain):
    symbol_table = chain.__code__.context.symbol_table.parent

    if symbol_table:
        result = {}

        while symbol_table:
            result |= symbol_table.symbols
            symbol_table = symbol_table.parent

        return result

    else:
        return chain.__code__.context.symbol_table.symbols

def locals(chain):
    return chain.__code__.context.symbol_table.symbols

def vars(chain, object=None):
    if object is None:
        return chain.__code__.context.symbol_table.symbols

    from builtins import vars

    return vars(object)

def dir(chain, *args):
    if len(args) == 0:
        return sorted(chain.__code__.context.symbol_table.symbols.keys())

    from builtins import dir

    return dir(*args)

def exec(chain, source, globals=None):
    if not isinstance(globals, (type(None), dict)):
        raise TypeError("exec(): globals must be dict")

    from .buffer import PysFileBuffer
    from .runner import pys_runner
    from .utils import build_symbol_table

    file = PysFileBuffer(source, '<exec>')

    result = pys_runner(
        file=file,
        mode='exec',
        flags=chain.__code__.flags,
        symbol_table=chain.__code__.context.symbol_table if globals is None else build_symbol_table(file, globals),
        context_parent=chain.__code__.context,
        context_parent_entry_position=chain.__code__.position
    )

    if result.error:
        from .exceptions import PysShouldReturn
        from .results import PysRunTimeResult

        raise PysShouldReturn(PysRunTimeResult().failure(result.error))

def eval(chain, source, globals=None):
    if not isinstance(globals, (type(None), dict)):
        raise TypeError("eval(): globals must be dict")

    from .buffer import PysFileBuffer
    from .runner import pys_runner
    from .utils import build_symbol_table

    file = PysFileBuffer(source, '<eval>')

    result = pys_runner(
        file=file,
        mode='eval',
        flags=chain.__code__.flags,
        symbol_table=chain.__code__.context.symbol_table if globals is None else build_symbol_table(file, globals),
        context_parent=chain.__code__.context,
        context_parent_entry_position=chain.__code__.position
    )

    if result.error:
        from .exceptions import PysShouldReturn
        from .results import PysRunTimeResult

        raise PysShouldReturn(PysRunTimeResult().failure(result.error))

    return result.result

def ce(a, b, *, rel_tol=1e-9, abs_tol=0):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        from math import isclose
        return isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    from .utils import supported_method

    success, result = supported_method(a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = supported_method(b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)

    if not success:
        raise TypeError(
            "unsupported operand type(s) for ~= or ce(): {!r} and {!r}".format(
                type(a).__name__,
                type(b).__name__
            )
        )

    return result

def nce(a, b, *, rel_tol=1e-9, abs_tol=0):
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        from math import isclose
        return not isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)

    from .utils import supported_method

    success, result = supported_method(a, '__nce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
    if not success:
        success, result = supported_method(b, '__nce__', a, rel_tol=rel_tol, abs_tol=abs_tol)
        if not success:
            success, result = supported_method(a, '__ce__', b, rel_tol=rel_tol, abs_tol=abs_tol)
            if not success:
                success, result = supported_method(b, '__ce__', a, rel_tol=rel_tol, abs_tol=abs_tol)

            result = not result

    if not success:
        raise TypeError(
            "unsupported operand type(s) for ~! or nce(): {!r} and {!r}".format(
                type(a).__name__,
                type(b).__name__
            )
        )

    return result

def increment(object):
    if isinstance(object, (int, float)):
        return object + 1

    from .utils import supported_method

    success, result = supported_method(object, '__increment__')

    if not success:
        raise TypeError("unsupported operand type(s) for ++ or increment(): {!r}".format(type(object).__name__))

    return result

def decrement(object):
    if isinstance(object, (int, float)):
        return object - 1

    from .utils import supported_method

    success, result = supported_method(object, '__decrement__')

    if not success:
        raise TypeError("unsupported operand type(s) for -- or decrement(): {!r}".format(type(object).__name__))

    return result

def comprehension(init, wrap, condition=None):
    if not callable(wrap):
        raise TypeError("comprehension(): wrap must be callable")
    if not (condition is None or callable(condition)):
        raise TypeError("comprehension(): condition must be callable")

    return map(wrap, init if condition is None else filter(condition, init))

require = PysChainFunction(require)
globals = PysChainFunction(globals)
locals = PysChainFunction(locals)
vars = PysChainFunction(vars)
dir = PysChainFunction(dir)
exec = PysChainFunction(exec)
eval = PysChainFunction(eval)

pys_builtins = PysModule(
    'built-in',

    "Built-in functions, types, exceptions, and other objects.\n\n"
    "This module provides direct access to all 'built-in' identifiers of PyScript and Python."
)

pys_builtins.__file__ = __file__

pys_builtins.license = license
pys_builtins.pyimport = pyimport
pys_builtins.require = require
pys_builtins.globals = globals
pys_builtins.locals = locals
pys_builtins.vars = vars
pys_builtins.dir = dir
pys_builtins.exec = exec
pys_builtins.eval = eval
pys_builtins.ce = ce
pys_builtins.nce = nce
pys_builtins.increment = increment
pys_builtins.decrement = decrement
pys_builtins.comprehension = comprehension
pys_builtins.isobjectof = isobjectof

import builtins

_blacklist = {'compile', 'copyright', 'credits', 'dir', 'eval', 'exec', 'globals', 'license', 'locals', 'vars'}

for name in dir(builtins):
    if not (name.startswith('_') or name in _blacklist):
        setattr(pys_builtins, name, getattr(builtins, name))

del builtins, PysModule, PysChainFunction, _Printer, _blacklist, name