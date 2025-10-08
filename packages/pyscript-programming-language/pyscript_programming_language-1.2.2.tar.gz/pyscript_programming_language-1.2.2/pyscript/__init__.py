import sys

if sys.version_info < (3, 5):
    raise ImportError("PyScript: Python version 3.5 and above is required to run PyScript")

from . import core

from .core.constants import DEFAULT, OPTIMIZE, SILENT, RETRES
from .core.highlight import HLFMT_HTML, HLFMT_ANSI, pys_highlight
from .core.runner import pys_exec, pys_eval
from .core.version import __version__, __date__

__all__ = [
    'core',
    'DEFAULT',
    'OPTIMIZE',
    'SILENT',
    'RETRES',
    'HLFMT_HTML',
    'HLFMT_ANSI',
    'pys_highlight',
    'pys_exec',
    'pys_eval'
]

del sys