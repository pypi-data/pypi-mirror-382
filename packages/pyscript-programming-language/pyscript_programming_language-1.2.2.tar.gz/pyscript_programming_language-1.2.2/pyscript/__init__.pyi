from typing import TYPE_CHECKING, Any, Callable, Dict, List, Literal, Union, Optional

if TYPE_CHECKING:
    from .core.buffer import PysFileBuffer
    from .core.highlight import _HighlightFormatter
    from .core.position import PysPosition
    from .core.symtab import PysSymbolTable

    from io import IOBase

from . import core

DEFAULT: int
OPTIMIZE: int
SILENT: int
RETRES: int

HLFMT_HTML: _HighlightFormatter
HLFMT_ANSI: _HighlightFormatter

def pys_highlight(
    source: Union[str, bytes, bytearray, IOBase, PysFileBuffer],
    format: Optional[Callable[[
        Literal[
            'start',
            'bracket-unmatch',
            'identifier', 'identifier-const', 'identifier-call', 'identifier-class',
            'keyword', 'keyword-identifier',
            'number', 'string', 'comment', 'newline',
            'default',
            'end'
        ], PysPosition, str], str]] = None,
    max_parenthesis_level: int = 3,
    flags: int = DEFAULT
) -> str: ...

def pys_exec(
    source: Union[str, bytes, bytearray, IOBase, PysFileBuffer],
    globals: Optional[Union[Dict[str, Any], PysSymbolTable]] = None,
    flags: int = DEFAULT
) -> None: ...

def pys_eval(
    source: Union[str, bytes, bytearray, IOBase, PysFileBuffer],
    globals: Optional[Union[Dict[str, Any], PysSymbolTable]] = None,
    flags: int = DEFAULT
) -> Any: ...

__version__: str
__date__: str
__all__: List[str]