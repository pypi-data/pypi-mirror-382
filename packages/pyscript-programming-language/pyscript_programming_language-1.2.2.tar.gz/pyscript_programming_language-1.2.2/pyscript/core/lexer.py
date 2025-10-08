from .bases import Pys
from .constants import TOKENS, KEYWORDS
from .context import PysContext
from .exceptions import PysException
from .position import PysPosition
from .token import PysToken

from unicodedata import lookup as unicode_lookup

import sys

class PysLexer(Pys):

    def __init__(self, file, context_parent=None, context_parent_entry_position=None, allowed_comment_token=False):
        self.file = file
        self.context_parent = context_parent
        self.context_parent_entry_position = context_parent_entry_position
        self.allowed_comment_token = allowed_comment_token

    def update_current_char(self):
        self.current_char = self.file.text[self.index] if 0 <= self.index < len(self.file.text) else None

    def advance(self):
        if self.error is None:
            self.index += 1
            self.update_current_char()

    def reverse(self, amount=1):
        if self.error is None:
            self.index -= amount
            self.update_current_char()

    def add_token(self, type, start=None, value=None):
        if self.error is None:

            if start is None:
                start = self.index
                end = self.index + 1
            else:
                end = self.index

            self.tokens.append(PysToken(type, PysPosition(self.file, start, end), value))

    def throw(self, start, message, end=None):
        if self.error is None:
            self.current_char = None
            self.tokens = []
            self.error = PysException(
                SyntaxError(message),
                PysContext(
                    name=None,
                    file=self.file,
                    parent=self.context_parent,
                    parent_entry_position=self.context_parent_entry_position
                ),
                PysPosition(self.file, start, end or self.index)
            )

    def not_eof(self):
        return self.current_char is not None

    def char_eq(self, character):
        return self.not_eof() and self.current_char == character

    def char_ne(self, character):
        return self.not_eof() and self.current_char != character

    def char_in(self, characters):
        return self.not_eof() and self.current_char in characters

    def char_are(self, string_method, *args, **kwargs):
        return self.not_eof() and getattr(self.current_char, string_method)(*args, **kwargs)

    def make_tokens(self):
        self.index = -1
        self.tokens = []
        self.error = None
        self.current_char = None

        self.advance()

        while self.not_eof():

            if self.char_eq('\n'):
                self.add_token(TOKENS['NEWLINE'])
                self.advance()

            elif self.char_eq('\\'):
                self.make_back_slash()

            elif self.char_are('isspace'):
                self.advance()

            elif self.char_in('0123456789.'):
                self.make_number()

            elif self.char_in('BRbr"\''):
                self.make_string()

            elif self.char_are('isidentifier'):
                self.make_identifier()

            elif self.char_eq('$'):
                self.make_dollar()

            elif self.char_eq('+'):
                self.make_plus()

            elif self.char_eq('-'):
                self.make_minus()

            elif self.char_eq('*'):
                self.make_mul()

            elif self.char_eq('/'):
                self.make_div()

            elif self.char_eq('%'):
                self.make_mod()

            elif self.char_eq('@'):
                self.make_at()

            elif self.char_eq('&'):
                self.make_and()

            elif self.char_eq('|'):
                self.make_or()

            elif self.char_eq('^'):
                self.make_xor()

            elif self.char_eq('~'):
                self.make_not()

            elif self.char_eq('='):
                self.make_equal()

            elif self.char_eq('!'):
                self.make_not_equal()

            elif self.char_eq('<'):
                self.make_lt()

            elif self.char_eq('>'):
                self.make_gt()

            elif self.char_eq('?'):
                self.make_question()

            elif self.char_eq('#'):
                self.make_comment()

            elif self.char_eq('('):
                self.add_token(TOKENS['LPAREN'])
                self.advance()

            elif self.char_eq(')'):
                self.add_token(TOKENS['RPAREN'])
                self.advance()

            elif self.char_eq('['):
                self.add_token(TOKENS['LSQUARE'])
                self.advance()

            elif self.char_eq(']'):
                self.add_token(TOKENS['RSQUARE'])
                self.advance()

            elif self.char_eq('{'):
                self.add_token(TOKENS['LBRACE'])
                self.advance()

            elif self.char_eq('}'):
                self.add_token(TOKENS['RBRACE'])
                self.advance()

            elif self.char_eq(':'):
                self.add_token(TOKENS['COLON'])
                self.advance()

            elif self.char_eq(','):
                self.add_token(TOKENS['COMMA'])
                self.advance()

            elif self.char_eq(';'):
                self.add_token(TOKENS['SEMICOLON'])
                self.advance()

            else:
                char = self.current_char

                self.advance()
                self.throw(self.index - 1, "invalid character '{}' (U+{:08X})".format(char, ord(char)))

        self.add_token(TOKENS['EOF'])

        return self.tokens, self.error

    def make_back_slash(self):
        self.advance()

        if self.char_ne('\n'):
            self.advance()
            self.throw(self.index - 1, "unexpected character after line continuation character")

        self.advance()

    def make_number(self):
        start = self.index
        format = int
        number = ''

        is_scientific = False
        is_complex = False
        is_underscore = False

        if self.char_eq('.'):
            format = float
            number = '.'

            self.advance()

            if self.file.text[self.index:self.index + 2] == '..':
                self.advance()
                self.advance()
                self.add_token(TOKENS['ELLIPSIS'], start)
                return

            elif not self.char_in('0123456789'):
                self.add_token(TOKENS['DOT'], start)
                return

        while self.char_in('0123456789'):
            number += self.current_char
            self.advance()

            is_underscore = False

            if self.char_eq('_'):
                is_underscore = True
                self.advance()

            elif self.char_eq('.') and not is_scientific and format is int:
                format = float

                number += '.'
                self.advance()

            elif self.char_in('BOXbox') and not is_scientific:
                if number != '0':
                    self.throw(start, "invalid decimal literal")
                    return

                format = str
                number = ''

                character_base = self.char_are('lower')

                if character_base == 'b':
                    base = 2
                    literal = '01'
                elif character_base == 'o':
                    base = 8
                    literal = '01234567'
                elif character_base == 'x':
                    base = 16
                    literal = '0123456789ABCDEFabcdef'

                self.advance()

                while self.char_in(literal):
                    number += self.current_char
                    self.advance()

                    is_underscore = False

                    if self.char_eq('_'):
                        is_underscore = True
                        self.advance()

                if not number:
                    self.throw(self.index - 1, "invalid decimal literal")

                if self.char_in('jJ'):
                    is_complex = True
                    self.advance()

                break

            elif self.char_in('eE') and not is_scientific:
                format = float
                is_scientific = True
                number += 'e'

                self.advance()

                if self.char_in('+-'):
                    number += self.current_char
                    self.advance()

            elif self.char_in('jJ'):
                is_complex = True
                self.advance()
                break

        if is_underscore or (is_scientific and number.endswith(('e', '-', '+'))):
            self.throw(self.index - 1, "invalid decimal literal")

        if self.char_eq('.'):
            self.advance()

            if format is float or is_complex or is_scientific:
                self.throw(self.index - 1, "invalid decimal literal")

            format = float

        if self.error is None:

            def wrap(obj, *args):
                result = obj(number, *args)
                return complex(0, result) if is_complex else result

            if format is float:
                self.add_token(TOKENS['NUMBER'], start, wrap(float))

            elif format is str:
                self.add_token(TOKENS['NUMBER'], start, wrap(int, base))

            elif format is int:
                self.add_token(TOKENS['NUMBER'], start, wrap(int))

    def make_string(self):
        string = ''
        start = self.index
        is_bytes = False
        is_raw = False

        if self.char_in('BRbr'):
            if self.char_in('Bb'):
                is_bytes = True
                self.advance()

            if self.char_in('Rr'):
                is_raw = True
                self.advance()

            if not self.char_in('"\''):
                self.reverse(self.index - start)
                self.make_identifier()
                return

        prefix = self.current_char

        def triple_quote():
            return self.file.text[self.index:self.index + 3] == prefix * 3

        is_triple_quote = triple_quote()
        warning_displayed = False
        decoded_error_message = None

        def decode_error(message):
            nonlocal decoded_error_message
            if decoded_error_message is None:
                decoded_error_message = message

        self.advance()

        if is_triple_quote:
            self.advance()
            self.advance()

        while self.not_eof() and not (triple_quote() if is_triple_quote else self.char_in(prefix + '\n')):

            if self.char_eq('\\'):
                self.advance()

                if is_raw:
                    string += '\\'
                    if self.char_in('\\\'"\n'):
                        string += self.current_char
                        self.advance()

                elif self.char_in('\\\'"nrtbfav\n'):
                    if self.char_in('\\\'"'):
                        string += self.current_char
                    elif self.char_eq('n'):
                        string += '\n'
                    elif self.char_eq('r'):
                        string += '\r'
                    elif self.char_eq('t'):
                        string += '\t'
                    elif self.char_eq('b'):
                        string += '\b'
                    elif self.char_eq('f'):
                        string += '\f'
                    elif self.char_eq('a'):
                        string += '\a'
                    elif self.char_eq('v'):
                        string += '\v'

                    self.advance()

                elif decoded_error_message is None:
                    escape = ''

                    if self.char_in('01234567'):

                        while self.char_in('01234567') and len(escape) < 3:
                            escape += self.current_char
                            self.advance()

                        string += chr(int(escape, 8))

                    elif self.char_in('xuU'):
                        base = self.current_char

                        if base == 'x':
                            length = 2
                        elif base == 'u':
                            length = 4
                        elif base == 'U':
                            length = 8

                        self.advance()

                        while self.char_in('0123456789ABCDEFabcdef') and len(escape) < length:
                            escape += self.current_char
                            self.advance()

                        if len(escape) != length:
                            decode_error("codec can't decode bytes, truncated \\{}{} escape".format(base, 'X' * length))

                        else:
                            try:
                                string += chr(int(escape, 16))
                            except:
                                decode_error("codec can't decode bytes: illegal Unicode character")

                    elif self.char_eq('N'):
                        self.advance()

                        if self.current_char != '{':
                            decode_error("malformed \\N character escape")
                            continue

                        self.advance()

                        while self.char_ne('}'):
                            escape += self.current_char
                            self.advance()

                        if self.current_char == '}':
                            try:
                                string += unicode_lookup(escape)
                            except:
                                decode_error("codec can't decode bytes, unknown Unicode character name")

                            self.advance()

                        else:
                            decode_error("malformed \\N character escape")

                    else:
                        if not self.not_eof():
                            string += '\\'
                            break

                        if not warning_displayed:
                            warning_displayed = True
                            print(
                                "SyntaxWarning: invalid escape sequence '\\{}'".format(self.current_char),
                                file=sys.stderr
                            )

                        string += '\\' + self.current_char
                        self.advance()

            else:
                string += self.current_char
                self.advance()

        if not (triple_quote() if is_triple_quote else self.char_eq(prefix)):
            self.throw(start, "unterminated bytes literal" if is_bytes else "unterminated string literal", start + 1)

        elif decoded_error_message is not None:
            self.advance()
            self.throw(start, decoded_error_message)

        else:
            self.advance()

            if is_triple_quote:
                self.advance()
                self.advance()

            try:
                self.add_token(TOKENS['STRING'], start, string.encode('ascii') if is_bytes else string)
            except:
                self.throw(start, "invalid bytes literal")

    def make_identifier(self, as_identifier=False, start=None):
        start = start if as_identifier else self.index
        name = ''

        while self.not_eof() and (name + self.current_char).isidentifier():
            name += self.current_char
            self.advance()

        self.add_token(
            TOKENS['KEYWORD']
                if not as_identifier and name in KEYWORDS.values() else
            TOKENS['IDENTIFIER'],
            start,
            name
        )

    def make_dollar(self):
        start = self.index

        self.advance()

        while self.char_ne('\n') and self.char_are('isspace'):
            self.advance()

        if not self.char_are('isidentifier'):
            self.advance()
            self.throw(self.index - 1, "expected identifier")

        self.make_identifier(as_identifier=True, start=start)

    def make_plus(self):
        start = self.index
        type = TOKENS['PLUS']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EPLUS']
            self.advance()

        elif self.char_eq('+'):
            type = TOKENS['INCREMENT']
            self.advance()

        self.add_token(type, start)

    def make_minus(self):
        start = self.index
        type = TOKENS['MINUS']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EMINUS']
            self.advance()

        elif self.char_eq('-'):
            type = TOKENS['DECREMENT']
            self.advance()

        self.add_token(type, start)

    def make_mul(self):
        start = self.index
        type = TOKENS['MUL']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EMUL']
            self.advance()

        elif self.char_eq('*'):
            type = TOKENS['POW']
            self.advance()

        if type == TOKENS['POW'] and self.char_eq('='):
            type = TOKENS['EPOW']
            self.advance()

        self.add_token(type, start)

    def make_div(self):
        start = self.index
        type = TOKENS['DIV']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EDIV']
            self.advance()

        elif self.char_eq('/'):
            type = TOKENS['FDIV']
            self.advance()

        if type == TOKENS['FDIV'] and self.char_eq('='):
            type = TOKENS['EFDIV']
            self.advance()

        self.add_token(type, start)

    def make_mod(self):
        start = self.index
        type = TOKENS['MOD']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EMOD']
            self.advance()

        self.add_token(type, start)

    def make_at(self):
        start = self.index
        type = TOKENS['AT']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EAT']
            self.advance()

        self.add_token(type, start)

    def make_and(self):
        start = self.index
        type = TOKENS['AND']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EAND']
            self.advance()

        self.add_token(type, start)

    def make_or(self):
        start = self.index
        type = TOKENS['OR']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EOR']
            self.advance()

        self.add_token(type, start)

    def make_xor(self):
        start = self.index
        type = TOKENS['XOR']

        self.advance()

        if self.current_char == '=':
            type = TOKENS['EXOR']
            self.advance()

        self.add_token(type, start)

    def make_not(self):
        start = self.index
        type = TOKENS['NOT']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['CE']
            self.advance()
        elif self.char_eq('!'):
            type = TOKENS['NCE']
            self.advance()

        self.add_token(type, start)

    def make_equal(self):
        start = self.index
        type = TOKENS['EQ']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['EE']
            self.advance()

        self.add_token(type, start)

    def make_not_equal(self):
        start = self.index
        type = TOKENS['NE']

        self.advance()

        if self.char_ne('='):
            self.advance()
            self.throw(self.index - 1, "expected '='")

        self.advance()
        self.add_token(type, start)

    def make_lt(self):
        start = self.index
        type = TOKENS['LT']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['LTE']
            self.advance()
        elif self.char_eq('<'):
            type = TOKENS['LSHIFT']
            self.advance()

        if type == TOKENS['LSHIFT'] and self.char_eq('='):
            type = TOKENS['ELSHIFT']
            self.advance()

        self.add_token(type, start)

    def make_gt(self):
        start = self.index
        type = TOKENS['GT']

        self.advance()

        if self.char_eq('='):
            type = TOKENS['GTE']
            self.advance()
        elif self.char_eq('>'):
            type = TOKENS['RSHIFT']
            self.advance()

        if type == TOKENS['RSHIFT'] and self.char_eq('='):
            type = TOKENS['ERSHIFT']
            self.advance()

        self.add_token(type, start)

    def make_question(self):
        start = self.index
        type = TOKENS['QUESTION']

        self.advance()

        if self.char_eq('?'):
            type = TOKENS['NULLISH']
            self.advance()

        self.add_token(type, start)

    def make_comment(self):
        start = self.index
        comment = ''

        self.advance()

        while self.char_ne('\n'):
            comment += self.current_char
            self.advance()

        if self.allowed_comment_token:
            self.add_token(TOKENS['COMMENT'], start, comment)