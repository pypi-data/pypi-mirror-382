from .bases import Pys
from .buffer import PysFileBuffer
from .constants import TOKENS, KEYWORDS, HIGHLIGHT, DEFAULT, SILENT
from .lexer import PysLexer
from .position import PysPosition
from .pysbuiltins import pys_builtins
from .utils import parenthesises_map, sanitize_newline

from html import escape as html_escape

class _HighlightFormatter(Pys):

    def __init__(self, content_block, open_block, close_block, newline_block):
        self.content_block = content_block
        self.open_block = open_block
        self.close_block = close_block
        self.newline_block = newline_block

        self._type = 'start'
        self._open = False

    def __call__(self, *args, **kwargs):
        return self.formater(*args, **kwargs)

    def formater(self, type, position, content):
        contented = self.content_block(position, content)
        result = ''

        if type == 'newline':
            if self._open:
                result += self.close_block(position, self._type)
                self._open = False

            result += self.newline_block(position)

        elif type == 'end':
            if self._open:
                result += self.close_block(position, self._type)
                self._open = False

        elif type == self._type and self._open:
            result += contented

        else:
            if self._open:
                result += self.close_block(position, self._type)

            result += self.open_block(position, type)
            result += contented

            self._open = True

        self._type = type
        return result

def _ansi_open_block(position, type):
    color = HIGHLIGHT.get(type, 'default')

    return '\x1b[38;2;{};{};{}m'.format(
        int(color[1:3], 16),
        int(color[3:5], 16),
        int(color[5:7], 16)
    )

HLFMT_HTML = _HighlightFormatter(
    lambda position, content: sanitize_newline('<br>', html_escape(content)),
    lambda position, type: '<span style="color:{}">'.format(HIGHLIGHT.get(type, 'default')),
    lambda position, type: '</span>',
    lambda position: '<br>'
)

HLFMT_ANSI = _HighlightFormatter(
    lambda position, content: sanitize_newline('\n', content),
    _ansi_open_block,
    lambda position, type: '\x1b[0m',
    lambda position: '\n'
)

def pys_highlight(source, format=None, max_parenthesis_level=3, flags=DEFAULT):
    """
    Highlight a PyScript code from source given.

    Parameters
    ----------
    source: A valid PyScript (Lexer/Tokenize) source code.

    format: A function to format the code form.

    max_parenthesis_level: Maximum difference level of parentheses (with circular indexing).

    flags: A special flags.
    """

    file = PysFileBuffer(source)

    if format is None:
        format = HLFMT_HTML
    elif not callable(format):
        raise TypeError("pys_highlight(): format must be callable")

    if not isinstance(max_parenthesis_level, int):
        raise TypeError("pys_highlight(): max_parenthesis_level must be integer")
    elif max_parenthesis_level < 0:
        raise ValueError("pys_highlight(): max_parenthesis_level must be grather than 0")

    lexer = PysLexer(file, allowed_comment_token=True)
    tokens, error = lexer.make_tokens()

    if error and not (flags & SILENT):
        raise error.exception

    result = ''
    last_index = 0
    parenthesis_level = 0

    parenthesises_level = {
        TOKENS['RPAREN']: 0,
        TOKENS['RSQUARE']: 0,
        TOKENS['RBRACE']: 0
    }

    for i, token in enumerate(tokens):

        if token.type in (TOKENS['RPAREN'], TOKENS['RSQUARE'], TOKENS['RBRACE']):
            parenthesises_level[token.type] -= 1
            parenthesis_level -= 1

        if token.type == TOKENS['EOF']:
            type_fmt = 'end'

        elif token.type == TOKENS['KEYWORD']:
            type_fmt = 'keyword-identifier' if token.value in {
                KEYWORDS['of'], KEYWORDS['in'], KEYWORDS['is'],
                KEYWORDS['and'], KEYWORDS['or'], KEYWORDS['not'],
                KEYWORDS['False'], KEYWORDS['None'], KEYWORDS['True']
            } else 'keyword'

        elif token.type == TOKENS['NUMBER']:
            type_fmt = 'number'

        elif token.type == TOKENS['STRING']:
            type_fmt = 'string'

        elif token.type == TOKENS['IDENTIFIER']:
            obj = getattr(pys_builtins, token.value, None)

            if isinstance(obj, type):
                type_fmt = 'identifier-class'
            elif callable(obj):
                type_fmt = 'identifier-call'
            else:
                type_fmt = 'identifier-const' if token.value.isupper() else 'identifier'

                if (i + 1 < len(tokens) and tokens[i + 1].type == TOKENS['LPAREN']):
                    type_fmt = 'identifier-call'

                j = i - 1
                while j > 0 and tokens[j].type == TOKENS['NEWLINE']:
                    j -= 1

                if tokens[j].match(TOKENS['KEYWORD'], KEYWORDS['class']):
                    type_fmt = 'identifier-class'
                elif tokens[j].match(TOKENS['KEYWORD'], KEYWORDS['func']):
                    type_fmt = 'identifier-call'

        elif token.type in (
            TOKENS['RPAREN'], TOKENS['RSQUARE'], TOKENS['RBRACE'],
            TOKENS['LPAREN'], TOKENS['LSQUARE'], TOKENS['LBRACE']
        ):
            type_fmt = 'parenthesis-{}'.format(
                'unmatch'
                if
                    parenthesises_level[parenthesises_map.get(token.type, token.type)] < 0 or
                    parenthesis_level < 0
                else
                parenthesis_level % max_parenthesis_level
            )

        elif token.type == TOKENS['NEWLINE']:
            type_fmt = 'newline'

        elif token.type == TOKENS['COMMENT']:
            type_fmt = 'comment'

        else:
            type_fmt = 'default'

        space = file.text[last_index:token.position.start]
        if space:
            result += format('default', PysPosition(token.position.file, last_index, token.position.start), space)

        result += format(type_fmt, token.position, file.text[token.position.start:token.position.end])

        last_index = token.position.end

        if token.type in (TOKENS['LPAREN'], TOKENS['LSQUARE'], TOKENS['LBRACE']):
            parenthesises_level[parenthesises_map[token.type]] += 1
            parenthesis_level += 1

        if token.type == TOKENS['EOF']:
            break

    return result

del _ansi_open_block