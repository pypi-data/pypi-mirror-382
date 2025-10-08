from .cache import library, hook
from .constants import LIBRARY_PATH, TOKENS, KEYWORDS

try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable

from inspect import currentframe
from json import detect_encoding
from io import IOBase

import operator
import sys
import os

inplace_functions_map = {
    TOKENS['EPLUS']: operator.iadd,
    TOKENS['EMINUS']: operator.isub,
    TOKENS['EMUL']: operator.imul,
    TOKENS['EDIV']: operator.itruediv,
    TOKENS['EFDIV']: operator.ifloordiv,
    TOKENS['EPOW']: operator.ipow,
    TOKENS['EAT']: operator.imatmul,
    TOKENS['EMOD']: operator.imod,
    TOKENS['EAND']: operator.iadd,
    TOKENS['EOR']: operator.ior,
    TOKENS['EXOR']: operator.ixor,
    TOKENS['ELSHIFT']: operator.ilshift,
    TOKENS['ERSHIFT']: operator.irshift
}

keyword_identifiers_map = {
    KEYWORDS['True']: True,
    KEYWORDS['False']: False,
    KEYWORDS['None']: None
}

parenthesises_sequence_map = {
    'tuple': TOKENS['LPAREN'],
    'list': TOKENS['LSQUARE'],
    'dict': TOKENS['LBRACE'],
    'set': TOKENS['LBRACE']
}

parenthesises_map = {
    TOKENS['LPAREN']: TOKENS['RPAREN'],
    TOKENS['LSQUARE']: TOKENS['RSQUARE'],
    TOKENS['LBRACE']: TOKENS['RBRACE']
}

def sanitize_newline(newline, string):
    return newline.join(string.splitlines())

def to_str(object):
    if isinstance(object, str):
        return sanitize_newline('\n', object)

    elif isinstance(object, (bytes, bytearray)):
        return to_str(object.decode(detect_encoding(object), 'surrogatepass'))

    elif isinstance(object, IOBase):
        if not object.readable():
            raise TypeError("unreadable IO")
        return to_str(object.read())

    elif isinstance(object, BaseException):
        return to_str(str(object))

    elif isinstance(object, type) and issubclass(object, BaseException):
        return ''

    raise TypeError('not a string')

def join_with_conjunction(sequence, func=None, conjunction='and'):
    if func is None:
        func = to_str

    if len(sequence) == 1:
        return func(sequence[0])
    elif len(sequence) == 2:
        return func(sequence[0]) + ' ' + conjunction + ' ' + func(sequence[1])

    result = ''

    for i, element in enumerate(sequence):
        if i == len(sequence) - 1:
            result += conjunction + ' ' + func(element)
        else:
            result += func(element) + ', '

    return result

def normalize_path(*paths, absolute=True):
    path = os.path.normpath(os.path.sep.join(map(to_str, paths)))
    if absolute:
        return os.path.abspath(path)
    return path

def get_similarity_ratio(string1, string2):
    string1 = [char for char in string1.lower() if not char.isspace()]
    string2 = [char for char in string2.lower() if not char.isspace()]

    bigram1 = set(string1[i] + string1[i + 1] for i in range(len(string1) - 1))
    bigram2 = set(string2[i] + string2[i + 1] for i in range(len(string2) - 1))

    max_bigrams_count = max(len(bigram1), len(bigram2))

    return 0.0 if max_bigrams_count == 0 else len(bigram1 & bigram2) / max_bigrams_count

def is_object_of(obj, class_or_tuple):
    return isinstance(obj, class_or_tuple) or (isinstance(obj, type) and issubclass(obj, class_or_tuple))

def supported_method(object, name, *args, **kwargs):
    from .singletons import undefined

    method = getattr(object, name, undefined)
    if method is undefined:
        return False, None

    if callable(method):

        try:

            result = method(*args, **kwargs)
            if result is NotImplemented:
                return False, None

            return True, result

        except NotImplementedError:
            return False, None

    return False, None

def get_caller_locals(deep=1):
    frame = currentframe()

    while deep > 0 and frame:
        frame = frame.f_back
        deep -= 1

    return frame.f_locals if frame else {}

def get_line_column_by_index(index, file):
    return file.text.count('\n', 0, index) + 1, index - file.text.rfind('\n', 0, index)

def format_highlighted_text_with_arrow(position):
    string = ''

    line_start, column_start = get_line_column_by_index(position.start, position.file)
    line_end, column_end = get_line_column_by_index(position.end, position.file)

    start = position.file.text.rfind('\n', 0, position.start) + 1
    end = position.file.text.find('\n', start + 1)
    if end == -1:
        end = len(position.file.text)

    if position.file.text[position.start:position.end] in {'', '\n'}:
        line = position.file.text[start:end].lstrip('\n')

        string += line + '\n'
        string += ' ' * len(line) + '^'

    else:
        lines = []
        count = line_end - line_start + 1

        for i in range(count):
            line = position.file.text[start:end].lstrip('\n')

            lines.append(
                (
                    line, len(line.lstrip()),
                    column_start - 1 if i == 0 else 0, column_end - 1 if i == count - 1 else len(line)
                )
            )

            start = end
            end = position.file.text.find('\n', start + 1)
            if end == -1:
                end = len(position.file.text)

        removed_indent = min(len(line) - no_indent for line, no_indent, _, _ in lines)

        for i, (line, no_indent, start, end) in enumerate(lines):
            line = line[removed_indent:]
            string += line + '\n'

            if i == 0:
                arrow = '^' * (end - start)
                line_arrow = ' ' * (start - removed_indent) + arrow

            else:
                indent = len(line) - no_indent
                arrow = '^' * (end - start - (removed_indent + indent))
                line_arrow = ' ' * indent + arrow

            if arrow and len(line_arrow) - 1 <= len(line):
                string += line_arrow + '\n'

    return string.replace('\t', ' ')

def generate_string_traceback(exception):
    frames = []
    stack = set()

    context = exception.context
    position = exception.position
    id_context = id(context)

    while context and id_context not in stack:
        stack.add(id_context)

        frames.append(
            '  File "{}", line {}{}\n    {}'.format(
                position.file.name,
                get_line_column_by_index(position.start, position.file)[0],
                '' if context.name is None else ', in {}'.format(context.name),
                '\n    '.join(format_highlighted_text_with_arrow(position).splitlines())
            )
        )

        position = context.parent_entry_position
        context = context.parent
        id_context = id(context)

    frames.reverse()

    strings_traceback = ''
    last_frame = ''
    found_duplicated_frame = 0

    for frame in frames:
        if frame == last_frame:
            found_duplicated_frame += 1

        else:
            if found_duplicated_frame > 0:
                strings_traceback += '  [Previous line repeated {} more times]\n'.format(found_duplicated_frame)
                found_duplicated_frame = 0

            strings_traceback += frame + '\n'
            last_frame = frame

    if found_duplicated_frame > 0:
        strings_traceback += '  [Previous line repeated {} more times]\n'.format(found_duplicated_frame)

    if id_context in stack:
        strings_traceback += '  [Previous lines repeated]\n'

    if isinstance(exception.exception, type):
        name = exception.exception.__name__
        message = ''
    else:
        name = type(exception.exception).__name__
        message = str(exception.exception)

    result = 'Traceback (most recent call last):\n{}{}'.format(strings_traceback, name)

    return result + ': ' + message if message else result

def build_symbol_table(file, globals=None):
    from .objects import PysModule
    from .singletons import undefined
    from .symtab import PysSymbolTable

    symtab = PysSymbolTable()

    symtab.module = PysModule(os.path.basename(file.name))

    if globals is not None:
        symtab.module.__dict__ = globals

    symtab.symbols = symtab.module.__dict__

    if symtab.get('__builtins__') is undefined:
        from .pysbuiltins import pys_builtins
        symtab.set('__builtins__', pys_builtins)

    if globals is None:
        symtab.set('__file__', file.name)

    return symtab

def print_display(value):
    if value is not None:
        print(repr(value))

def print_traceback(exception):
    for line in generate_string_traceback(exception).splitlines():
        print(line, file=sys.stderr)

hook.exception = print_traceback

try:
    for lib in os.listdir(LIBRARY_PATH):
        library.add(os.path.splitext(lib)[0])
except BaseException as e:
    print("Error: cannot load library folder {}: {}".format(LIBRARY_PATH, e), file=sys.stderr)