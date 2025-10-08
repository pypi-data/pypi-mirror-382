from .bases import Pys
from .constants import TOKENS, KEYWORDS, DEFAULT, REVERSE_POW_XOR
from .context import PysContext
from .exceptions import PysException
from .nodes import *
from .position import PysPosition
from .results import PysParserResult
from .token import PysToken
from .utils import parenthesises_sequence_map, parenthesises_map

class PysParser(Pys):

    def __init__(self, file, tokens, context_parent=None, context_parent_entry_position=None, future=DEFAULT):
        self.file = file
        self.tokens = tokens
        self.context = context_parent
        self.context_parent_entry_position = context_parent_entry_position
        self.future = future

        self.token_index = -1
        self.parenthesis_level = 0

        self.advance()

    def update_current_token(self):
        if 0 <= self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]

    def advance(self):
        self.token_index += 1
        self.update_current_token()

    def reverse(self, amount=1):
        self.token_index -= amount
        self.update_current_token()

    def error(self, message, position=None):
        return PysException(
            SyntaxError(message),
            PysContext(
                name=None,
                file=self.file,
                parent=self.context,
                parent_entry_position=self.context_parent_entry_position
            ),
            position or self.current_token.position
        )

    def parse(self, func=None):
        result = (func or self.statements)()

        if not result.error and self.current_token.type != TOKENS['EOF']:
            return result.failure(self.error("invalid syntax"))

        return result

    def statements(self):
        result = PysParserResult()
        start = self.current_token.position.start

        statements = []
        more_statements = True
        parenthesis_level = self.parenthesis_level

        self.parenthesis_level = 0

        while True:
            advance_count = self.skip(result, (TOKENS['NEWLINE'], TOKENS['SEMICOLON']))

            if not more_statements:
                if advance_count == 0:
                    break
                more_statements = True

            statement = result.try_register(self.statement())
            if result.error:
                return result

            if statement:
                statements.append(statement)
            else:
                self.reverse(result.to_reverse_count)

            more_statements = False

        self.parenthesis_level = parenthesis_level

        return result.success(
            PysSequenceNode(
                'statements',
                statements,
                PysPosition(self.file, start, self.current_token.position.end)
            )
        )

    def statement(self):
        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['from']):
            return self.from_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['import']):
            return self.import_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['if']):
            return self.if_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['switch']):
            return self.switch_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['try']):
            return self.try_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['for']):
            return self.for_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['while']):
            return self.while_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['do']):
            return self.do_while_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['class']):
            return self.class_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['return']):
            return self.return_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['del']):
            return self.del_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['throw']):
            return self.throw_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['assert']):
            return self.assert_expr()

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['continue']):
            result = PysParserResult()
            position = self.current_token.position

            result.register_advancement()
            self.advance()

            return result.success(PysContinueNode(position))

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['break']):
            result = PysParserResult()
            position = self.current_token.position

            result.register_advancement()
            self.advance()

            return result.success(PysBreakNode(position))

        elif self.current_token.type == TOKENS['AT']:
            result = PysParserResult()

            decorators = []

            while self.current_token.type == TOKENS['AT']:
                result.register_advancement()
                self.advance()

                decorators.append(result.register(self.expr(), True))
                if result.error:
                    return result

                self.skip(result, (TOKENS['NEWLINE'], TOKENS['SEMICOLON']))

            if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['func']):
                func_expr = result.register(self.func_expr())
                if result.error:
                    return result

                func_expr.decorators = decorators
                return result.success(func_expr)

            elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['class']):
                class_expr = result.register(self.class_expr())
                if result.error:
                    return result

                class_expr.decorators = decorators
                return result.success(class_expr)

            return result.failure(self.error("expected function or class declaration after decorator"))

        result = PysParserResult()

        assign_expr = result.register(self.assign_expr())
        if result.error:
            return result.failure(self.error("expected an expression or statement"), fatal=False)

        return result.success(assign_expr)

    def assign_expr(self):
        result = PysParserResult()

        variable = result.register(self.expr())
        if result.error:
            return result

        while self.current_token.type in (
            TOKENS['EQ'],
            TOKENS['EPLUS'],
            TOKENS['EMINUS'],
            TOKENS['EMUL'],
            TOKENS['EDIV'],
            TOKENS['EFDIV'],
            TOKENS['EMOD'],
            TOKENS['EAT'],
            TOKENS['EPOW'],
            TOKENS['EAND'],
            TOKENS['EOR'],
            TOKENS['EXOR'],
            TOKENS['ELSHIFT'],
            TOKENS['ERSHIFT']
        ):
            operand = (
                PysToken(
                    TOKENS['EPOW'] if self.current_token.type == TOKENS['EXOR'] else TOKENS['EXOR'],
                    self.current_token.position,
                    'reversed'
                )
                if self.future & REVERSE_POW_XOR and self.current_token.type in (TOKENS['EPOW'], TOKENS['EXOR']) else
                self.current_token
            )

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            value = result.register(self.assign_expr(), True)
            if result.error:
                return result

            variable = PysAssignNode(variable, operand, value)

        return result.success(variable)

    def expr(self):
        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['func']):
            return self.func_expr()

        return self.ternary()

    def ternary(self):
        result = PysParserResult()

        node = result.register(self.logic())
        if result.error:
            return result

        if self.current_token.type == TOKENS['QUESTION']:
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            valid = result.register(self.ternary(), True)
            if result.error:
                return result

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.error("expected ':'"))

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            invalid = result.register(self.ternary(), True)
            if result.error:
                return result

            return result.success(PysTernaryOperatorNode(node, valid, invalid))

        return result.success(node)

    def logic(self):
        return self.binary_operator(
            self.member,
            (
                (TOKENS['KEYWORD'], KEYWORDS['and']),
                (TOKENS['KEYWORD'], KEYWORDS['or']),
            )
        )

    def member(self):
        return self.chain_operator(
            self.comp,
            (
                (TOKENS['KEYWORD'], KEYWORDS['in']),
                (TOKENS['KEYWORD'], KEYWORDS['is']),
                (TOKENS['KEYWORD'], KEYWORDS['not'])
            ),
            is_member=True
        )

    def comp(self):
        token = self.current_token

        if token.match(TOKENS['KEYWORD'], KEYWORDS['not']):
            result = PysParserResult()

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            node = result.register(self.comp(), True)
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    token,
                    node,
                    operand_position='left'
                )
            )

        return self.chain_operator(
            self.bitwise,
            (
                TOKENS['EE'], TOKENS['NE'], TOKENS['CE'], TOKENS['NCE'],
                TOKENS['LT'], TOKENS['GT'], TOKENS['LTE'], TOKENS['GTE']
            )
        )

    def bitwise(self):
        return self.binary_operator(
            self.arith,
            (
                TOKENS['AND'], TOKENS['OR'],
                TOKENS['POW'] if self.future & REVERSE_POW_XOR else TOKENS['XOR'],
                TOKENS['LSHIFT'], TOKENS['RSHIFT']
            ),
            is_bitwise=True
        )

    def arith(self):
        return self.binary_operator(self.term, (TOKENS['PLUS'], TOKENS['MINUS']))

    def term(self):
        return self.binary_operator(
            self.factor,
            (TOKENS['MUL'], TOKENS['DIV'], TOKENS['FDIV'], TOKENS['MOD'], TOKENS['AT'])
        )

    def factor(self):
        result = PysParserResult()
        token = self.current_token

        if token.type in (TOKENS['PLUS'], TOKENS['MINUS'], TOKENS['NOT'], TOKENS['INCREMENT'], TOKENS['DECREMENT']):
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            node = result.register(self.factor(), True)
            if result.error:
                return result

            return result.success(
                PysUnaryOperatorNode(
                    token,
                    node,
                    operand_position='left'
                )
            )

        return self.power()

    def power(self):
        result = PysParserResult()

        left = result.register(self.nullish())
        if result.error:
            return result

        if self.current_token.type == (TOKENS['XOR'] if self.future & REVERSE_POW_XOR else TOKENS['POW']):
            operand = (
                PysToken(TOKENS['POW'], self.current_token.position, 'reversed')
                    if self.future & REVERSE_POW_XOR else
                self.current_token
            )

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            right = result.register(self.factor(), True)
            if result.error:
                return result

            left = PysBinaryOperatorNode(left, operand, right)

        return result.success(left)

    def nullish(self):
        return self.binary_operator(self.primary, (TOKENS['NULLISH'],))

    def primary(self):
        result = PysParserResult()
        start = self.current_token.position.start

        node = result.register(self.atom())
        if result.error:
            return result

        while self.current_token.type in (
            TOKENS['INCREMENT'],
            TOKENS['DECREMENT'],
            TOKENS['LPAREN'],
            TOKENS['LSQUARE'],
            TOKENS['DOT']
        ):

            if self.current_token.type in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
                operand = self.current_token

                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                node = PysUnaryOperatorNode(operand, node, operand_position='right')
                start = self.current_token.position.start

            elif self.current_token.type == TOKENS['LPAREN']:
                left_parenthesis_token = self.current_token

                self.parenthesis_level += 1

                result.register_advancement()
                self.advance()
                self.skip(result)

                seen_kwargs = False
                args = []

                while self.current_token.type not in parenthesises_map.values():

                    arg_or_keyword = result.register(self.expr(), True)
                    if result.error:
                        return result

                    if self.current_token.type == TOKENS['EQ']:
                        if not isinstance(arg_or_keyword, PysIdentifierNode):
                            return result.failure(
                                self.error("expected identifier (before '=')", arg_or_keyword.position)
                            )

                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        seen_kwargs = True

                    elif seen_kwargs:
                        return result.failure(self.error("expected '=' (follows keyword argument)"))

                    if seen_kwargs:
                        value = result.register(self.expr(), True)
                        if result.error:
                            return result

                        args.append((arg_or_keyword.token, value))

                    else:
                        args.append(arg_or_keyword)

                    self.skip(result)

                    if self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                    elif self.current_token.type not in parenthesises_map.values():
                        return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

                end = self.current_token.position.end

                self.close_parenthesis(result, left_parenthesis_token)
                if result.error:
                    return result

                self.parenthesis_level -= 1

                self.skip_expr(result)

                node = PysCallNode(node, args, PysPosition(self.file, start, end))
                start = self.current_token.position.start

            elif self.current_token.type == TOKENS['LSQUARE']:
                left_parenthesis_token = self.current_token
                start = self.current_token.position.start

                slices = []
                single_slice = True
                indices = [None, None, None]
                index = 1

                self.parenthesis_level += 1

                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    indices[0] = result.register(self.expr(), True)
                    if result.error:
                        return result

                    if self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        single_slice = False

                if not single_slice or self.current_token.type in parenthesises_map.values():
                    slices.append(indices[0])
                    index -= 1

                while self.current_token.type not in parenthesises_map.values():

                    if self.current_token.type != TOKENS['COLON']:
                        indices[index] = result.register(self.expr(), True)
                        if result.error:
                            return result

                        index += 1

                    single_index = self.current_token.type != TOKENS['COLON']

                    while index < 3 and self.current_token.type == TOKENS['COLON']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        if self.current_token.type in parenthesises_map.values():
                            break

                        indices[index] = result.try_register(self.expr())
                        if result.error:
                            return result

                        self.skip(result)
                        index += 1

                    if single_index:
                        slices.append(indices[0])
                    else:
                        slices.append(tuple(indices))

                    indices = [None, None, None]
                    index = 0

                    if self.current_token.type == TOKENS['COMMA']:
                        result.register_advancement()
                        self.advance()
                        self.skip(result)

                        single_slice = False

                    elif self.current_token.type not in parenthesises_map.values():
                        return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

                end = self.current_token.position.end

                self.close_parenthesis(result, left_parenthesis_token)
                if result.error:
                    return result

                self.parenthesis_level -= 1

                self.skip_expr(result)

                if single_slice:
                    slices = slices[0]

                node = PysSubscriptNode(node, slices, PysPosition(self.file, start, end))
                start = self.current_token.position.start

            elif self.current_token.type == TOKENS['DOT']:
                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                attribute = self.current_token
                start = self.current_token.position.start

                if attribute.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.error("expected identifier"))

                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                node = PysAttributeNode(node, attribute)

        return result.success(node)

    def atom(self):
        result = PysParserResult()
        token = self.current_token

        if token.matches(TOKENS['KEYWORD'], (KEYWORDS['True'], KEYWORDS['False'], KEYWORDS['None'])):
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            return result.success(PysKeywordNode(token))

        elif token.type == TOKENS['IDENTIFIER']:
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            return result.success(PysIdentifierNode(token))

        elif token.type == TOKENS['NUMBER']:
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            return result.success(PysNumberNode(token))

        elif token.type == TOKENS['STRING']:
            format = type(token.value)
            string = '' if format is str else b''

            while self.current_token.type == TOKENS['STRING']:
                if not isinstance(self.current_token.value, format):
                    return result.failure(
                        self.error(
                            "cannot mix bytes and nonbytes literals",
                            self.current_token.position
                        )
                    )

                string += self.current_token.value

                end = self.current_token.position.end

                result.register_advancement()
                self.advance()
                self.skip_expr(result)

            return result.success(
                PysStringNode(
                    PysToken(
                        TOKENS['STRING'],
                        PysPosition(self.file, token.position.start, end),
                        string
                    )
                )
            )

        elif token.type == TOKENS['LPAREN']:
            expr = result.register(self.sequence_expr('tuple'))
            if result.error:
                return result

            return result.success(expr)

        elif token.type == TOKENS['LSQUARE']:
            list_expr = result.register(self.sequence_expr('list'))
            if result.error:
                return result

            return result.success(list_expr)

        elif token.type == TOKENS['LBRACE']:
            dict_expr = result.try_register(self.sequence_expr('dict'))
            if result.error:
                return result

            if not dict_expr:
                self.reverse(result.to_reverse_count)

                set_expr = result.register(self.sequence_expr('set'))
                if result.error:
                    return result

                return result.success(set_expr)

            return result.success(dict_expr)

        elif token.type == TOKENS['ELLIPSIS']:
            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            return result.success(PysEllipsisNode(token.position))

        return result.failure(self.error("expected expression", token.position), fatal=False)

    def sequence_expr(self, type, should_sequence=False):
        result = PysParserResult()
        start = self.current_token.position.start

        elements = []

        left_parenthesis = parenthesises_sequence_map[type]

        if self.current_token.type != left_parenthesis:
            return result.failure(self.error("expected {!r}".format(chr(left_parenthesis))))

        left_parenthesis_token = self.current_token

        self.parenthesis_level += 1

        result.register_advancement()
        self.advance()
        self.skip(result)

        if type == 'dict':
            always_dict = False

            while self.current_token.type not in parenthesises_map.values():

                key = result.register(self.expr(), True)
                if result.error:
                    return result

                self.skip(result)

                if self.current_token.type != TOKENS['COLON']:
                    if not always_dict:
                        self.parenthesis_level -= 1

                    return result.failure(self.error("expected ':'"), fatal=always_dict)

                result.register_advancement()
                self.advance()
                self.skip(result)

                value = result.register(self.expr(), True)
                if result.error:
                    return result

                elements.append((key, value))

                always_dict = True

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                elif self.current_token.type not in parenthesises_map.values():
                    return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

        else:

            while self.current_token.type not in parenthesises_map.values():

                elements.append(result.register(self.expr(), True))
                if result.error:
                    return result

                self.skip(result)

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    should_sequence = True

                elif self.current_token.type not in parenthesises_map.values():
                    return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

        end = self.current_token.position.end

        self.close_parenthesis(result, left_parenthesis_token)
        if result.error:
            return result

        self.parenthesis_level -= 1

        self.skip_expr(result)

        if type == 'tuple' and not should_sequence and elements:
            return result.success(elements[0])

        return result.success(
            PysSequenceNode(
                type,
                elements,
                PysPosition(self.file, start, end)
            )
        )

    def from_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['from']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['from'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type not in (TOKENS['STRING'], TOKENS['IDENTIFIER']):
            return result.failure(self.error("expected string or identifier"))

        name = self.current_token

        result.register_advancement()
        self.advance()
        self.skip(result)

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['import']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['import'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        packages = []

        if self.current_token.type in parenthesises_map.keys():
            left_parenthesis_token = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

            while self.current_token.type not in parenthesises_map.values():

                if self.current_token.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.error("expected identifier"))

                package = self.current_token

                if name.value == '__future__':
                    push = result.register(self.proccess_future(package.value))
                    if result.error:
                        return result
                else:
                    push = True

                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['as']):
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                    if self.current_token.type != TOKENS['IDENTIFIER']:
                        return result.failure(self.error("expected identifier"))

                    as_package = self.current_token

                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                else:
                    as_package = None

                if self.current_token.type == TOKENS['COMMA']:
                    result.register_advancement()
                    self.advance()
                    self.skip(result)

                elif self.current_token.type not in parenthesises_map.values():
                    return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

                if push:
                    packages.append((package, as_package))

            if not packages:
                return result.failure(self.error("invalid syntax. At least need 1 package"))

            self.close_parenthesis(result, left_parenthesis_token)
            if result.error:
                return result

        elif self.current_token.type == TOKENS['IDENTIFIER']:
            package = self.current_token

            if name.value == '__future__':
                push = result.register(self.proccess_future(package.value))
                if result.error:
                    return result
            else:
                push = True

            result.register_advancement()
            self.advance()

            advance_count = self.skip(result)

            if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['as']):
                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.error("expected identifier"))

                as_package = self.current_token

                result.register_advancement()
                self.advance()

            else:
                as_package = None
                self.reverse(advance_count)

            if push:
                packages.append((package, as_package))

        elif self.current_token.type == TOKENS['MUL']:
            result.register_advancement()
            self.advance()

            packages = 'all'

        else:
            return result.failure(self.error("expected identifiers or '*'"))

        return result.success(PysImportNode((name, None), packages, position))

    def import_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['import']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['import'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type not in (TOKENS['STRING'], TOKENS['IDENTIFIER']):
            return result.failure(self.error("expected string or identifier"))

        name = self.current_token

        result.register_advancement()
        self.advance()

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['as']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.error("expected identifier"))

            as_name = self.current_token

            result.register_advancement()
            self.advance()

        else:
            as_name = None
            self.reverse(advance_count)

        return result.success(PysImportNode((name, as_name), [], position))

    def if_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        cases = result.register(self.if_expr_cases(KEYWORDS['if']))
        if result.error:
            return result

        return result.success(PysIfNode(cases[0], cases[1], position))

    def elif_expr(self):
        return self.if_expr_cases(KEYWORDS['elif'])

    def else_expr(self):
        result = PysParserResult()

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.stateblock(), True)
            if result.error:
                return result

            return result.success(else_body)

        return result.success(None)

    def elif_or_else_expr(self):
        result = PysParserResult()

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['elif']):
            all_cases = result.register(self.elif_expr())
            if result.error:
                return result

            return result.success(all_cases)

        else_body = result.register(self.else_expr())
        if result.error:
            return result

        return result.success(([], else_body))

    def if_expr_cases(self, case_keyword):
        result = PysParserResult()
        cases, else_body = [], None

        if not self.current_token.match(TOKENS['KEYWORD'], case_keyword):
            return result.failure(self.error("expected {!r}".format(case_keyword)))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.atom(), True)
        if result.error:
            return result

        self.skip(result)

        body = result.register(self.stateblock(), True)
        if result.error:
            return result

        cases.append((condition, body))

        advance_count = self.skip(result)

        if self.current_token.matches(TOKENS['KEYWORD'], (KEYWORDS['elif'], KEYWORDS['else'])):
            all_cases = result.register(self.elif_or_else_expr())
            if result.error:
                return result

            new_cases, else_body = all_cases
            cases.extend(new_cases)

        else:
            self.reverse(advance_count)

        return result.success((cases, else_body))

    def switch_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['switch']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['switch'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        target = result.register(self.atom(), True)
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.error("expected '{'"))

        left_parenthesis_token = self.current_token

        result.register_advancement()
        self.advance()
        self.skip(result)

        cases = result.register(self.case_or_default_expr())
        if result.error:
            return result

        self.close_parenthesis(result, left_parenthesis_token)
        if result.error:
            return result

        return result.success(PysSwitchNode(target, cases[0], cases[1], position))

    def case_expr(self):
        result = PysParserResult()
        cases, default_case = [], None

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['case']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['case'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        expr = result.register(self.atom(), True)
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type != TOKENS['COLON']:
            return result.failure(self.error("expected ':'"))

        result.register_advancement()
        self.advance()

        body = result.register(self.statements())
        if result.error:
            return result

        cases.append((expr, body))

        if self.current_token.matches(TOKENS['KEYWORD'], (KEYWORDS['case'], KEYWORDS['default'])):
            all_cases = result.register(self.case_or_default_expr())
            if result.error:
                return result

            new_cases, default_case = all_cases
            cases.extend(new_cases)

        return result.success((cases, default_case))

    def default_expr(self):
        result = PysParserResult()

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['default']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type != TOKENS['COLON']:
                return result.failure(self.error("expected ':'"))

            result.register_advancement()
            self.advance()

            body = result.register(self.statements())
            if result.error:
                return result

            return result.success(body)

        return result.success(None)

    def case_or_default_expr(self):
        result = PysParserResult()

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['case']):
            all_cases = result.register(self.case_expr())
            if result.error:
                return result

            return result.success(all_cases)

        default_body = result.register(self.default_expr())
        if result.error:
            return result

        return result.success(([], default_body))

    def try_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['try']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['try'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.register(self.stateblock(), True)
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['catch']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type == TOKENS['LPAREN']:
                left_parenthesis_token = self.current_token

                result.register_advancement()
                self.advance()
                self.skip(result)

                if self.current_token.type != TOKENS['IDENTIFIER']:
                    return result.failure(self.error("expected identifier"))

                error_variable = self.current_token

                result.register_advancement()
                self.advance()
                self.skip(result)

                self.close_parenthesis(result, left_parenthesis_token)
                if result.error:
                    return result

                self.skip(result)

            elif self.current_token.type == TOKENS['IDENTIFIER']:
                error_variable = self.current_token

                result.register_advancement()
                self.advance()
                self.skip(result)

            else:
                error_variable = None

            catch_body = result.register(self.stateblock(), True)
            if result.error:
                return result

            advance_count = self.skip(result)

        else:
            error_variable = None
            catch_body = None

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['finally']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            finally_body = result.register(self.stateblock(), True)
            if result.error:
                return result

        else:
            if not catch_body:
                return result.failure(
                    self.error("expected {!r} or {!r}".format(KEYWORDS['catch'], KEYWORDS['finally']))
                )

            finally_body = None
            self.reverse(advance_count)

        return result.success(PysTryNode(body, error_variable, catch_body, finally_body, position))

    def for_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['for']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['for'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['LPAREN']:
            return result.failure(self.error("expected '('"))

        left_parenthesis_token = self.current_token

        result.register_advancement()
        self.advance()
        self.skip(result)

        self.parenthesis_level += 1

        init_token_position = self.current_token.position

        init = result.try_register(self.assign_expr())
        if result.error:
            return result

        self.skip(result)

        if self.current_token.type == TOKENS['SEMICOLON']:
            foreach = False

            result.register_advancement()
            self.advance()
            self.skip(result)

            condition = result.try_register(self.expr())
            if result.error:
                return result

            self.skip(result)

            if self.current_token.type != TOKENS['SEMICOLON']:
                return result.failure(self.error("expected ';'"))

            result.register_advancement()
            self.advance()
            self.skip(result)

            update = result.try_register(self.assign_expr())
            if result.error:
                return result

        elif self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['of']):
            if init is None:
                return result.failure(self.error("expected expression", init_token_position))

            foreach = True

            result.register_advancement()
            self.advance()
            self.skip(result)

            iter = result.register(self.expr(), True)
            if result.error:
                return result

        else:
            return result.failure(self.error("expected assign expression or ';'"))

        self.skip(result)

        self.close_parenthesis(result, left_parenthesis_token)
        if result.error:
            return result

        self.parenthesis_level -= 1

        self.skip(result)

        body = result.try_register(self.stateblock())
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.stateblock(), True)
            if result.error:
                return result

        else:
            else_body = None
            self.reverse(advance_count)

        return result.success(
            PysForNode(
                (init, iter) if foreach else (init, condition, update),
                body,
                else_body,
                position
            )
        )

    def while_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['while']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['while'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.atom(), True)
        if result.error:
            return result

        self.skip(result)

        body = result.try_register(self.stateblock())
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.stateblock(), True)
            if result.error:
                return result

        else:
            else_body = None
            self.reverse(advance_count)

        return result.success(PysWhileNode(condition, body, else_body, position))

    def do_while_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['do']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['do'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        body = result.try_register(self.stateblock())
        if result.error:
            return result

        self.skip(result)

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['while']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['while'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.atom(), True)
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['else']):
            result.register_advancement()
            self.advance()
            self.skip(result)

            else_body = result.register(self.stateblock(), True)
            if result.error:
                return result

        else:
            else_body = None
            self.reverse(advance_count)

        return result.success(PysDoWhileNode(body, condition, else_body, position))

    def class_expr(self):
        result = PysParserResult()
        start = self.current_token.position.start

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['class']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['class'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type != TOKENS['IDENTIFIER']:
            return result.failure(self.error("expected identifier"))

        name = self.current_token
        end = self.current_token.position.end

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['LPAREN']:
            bases = result.register(self.sequence_expr('tuple', should_sequence=True))
            if result.error:
                return result

            end = bases.position.end
            bases = bases.elements

        else:
            bases = []

        if self.current_token.type != TOKENS['LBRACE']:
            return result.failure(self.error("expected '{"))

        left_parenthesis_token = self.current_token

        result.register_advancement()
        self.advance()

        body = result.register(self.statements())
        if result.error:
            return result

        self.close_parenthesis(result, left_parenthesis_token)
        if result.error:
            return result

        return result.success(PysClassNode(name, bases, body, PysPosition(self.file, start, end)))

    def func_expr(self):
        result = PysParserResult()
        start = self.current_token.position.start

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['func']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['func'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        if self.current_token.type == TOKENS['IDENTIFIER']:
            name = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

        else:
            name = None

        if self.current_token.type != TOKENS['LPAREN']:
            return result.failure(self.error("expected identifier or '('"))

        left_parenthesis_token = self.current_token

        self.parenthesis_level += 1

        result.register_advancement()
        self.advance()
        self.skip(result)

        seen_kwargs = False
        parameters = []

        while self.current_token.type not in parenthesises_map.values():

            if self.current_token.type != TOKENS['IDENTIFIER']:
                return result.failure(self.error("expected identifier"))

            key = self.current_token

            result.register_advancement()
            self.advance()
            self.skip(result)

            if self.current_token.type == TOKENS['EQ']:
                result.register_advancement()
                self.advance()
                self.skip(result)

                seen_kwargs = True

            elif seen_kwargs:
                return result.failure(self.error("expected '=' (follows keyword argument)"))

            if seen_kwargs:
                value = result.register(self.expr(), True)
                if result.error:
                    return result

                parameters.append((key, value))

            else:
                parameters.append(key)

            self.skip(result)

            if self.current_token.type == TOKENS['COMMA']:
                result.register_advancement()
                self.advance()
                self.skip(result)

            elif self.current_token.type not in parenthesises_map.values():
                return result.failure(self.error("invalid syntax. Perhaps you forgot a comma?"))

        end = self.current_token.position.end

        self.close_parenthesis(result, left_parenthesis_token)
        if result.error:
            return result

        self.parenthesis_level -= 1

        self.skip(result)

        body = result.register(self.stateblock(), True)
        if result.error:
            return result

        return result.success(
            PysFunctionNode(
                name,
                parameters,
                body,
                PysPosition(self.file, start, end)
            )
        )

    def return_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['return']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['return'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        value = result.try_register(self.expr())
        if result.error:
            return result

        if not value:
            self.reverse(result.to_reverse_count)

        return result.success(
            PysReturnNode(
                value,
                position
            )
        )

    def del_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['del']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['del'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        expr = result.register(self.expr(), True)
        if result.error:
            return result

        if isinstance(expr, PysSequenceNode):
            targets = expr.elements
            if not targets:
                return result.failure(self.error("empty object", expr.position))

        else:
            targets = [expr]

        return result.success(
            PysDeleteNode(
                targets,
                position
            )
        )

    def throw_expr(self):
        result = PysParserResult()
        position = self.current_token.position

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['throw']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['throw'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        target = result.register(self.expr(), True)
        if result.error:
            return result

        return result.success(PysThrowNode(target, position))

    def assert_expr(self):
        result = PysParserResult()

        if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['assert']):
            return result.failure(self.error("expected {!r}".format(KEYWORDS['assert'])))

        result.register_advancement()
        self.advance()
        self.skip(result)

        condition = result.register(self.expr(), True)
        if result.error:
            return result

        advance_count = self.skip(result)

        if self.current_token.type == TOKENS['COMMA']:
            result.register_advancement()
            self.advance()
            self.skip(result)

            message = result.register(self.expr(), True)
            if result.error:
                return result

        else:
            message = None
            self.reverse(advance_count)

        return result.success(
            PysAssertNode(
                condition,
                message
            )
        )

    def stateblock(self):
        result = PysParserResult()

        if self.current_token.type == TOKENS['LBRACE']:
            left_parenthesis_token = self.current_token

            result.register_advancement()
            self.advance()

            body = result.register(self.statements())
            if result.error:
                return result

            self.close_parenthesis(result, left_parenthesis_token)
            if result.error:
                return result

            return result.success(body)

        body = result.register(self.statement())
        if result.error:
            return result

        return result.success(body)

    def chain_operator(self, func, operators, is_member=False):
        result = PysParserResult()

        operations = []
        expressions = []

        expr = result.register(func())
        if result.error:
            return result

        while self.current_token.type in operators or (self.current_token.type, self.current_token.value) in operators:
            operations.append(self.current_token)
            expressions.append(expr)

            if is_member and self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['not']):
                result.register_advancement()
                self.advance()
                self.skip_expr(result)

                if not self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['in']):
                    return result.failure(self.error("expected {!r}".format(KEYWORDS['in'])))

                operations[-1] = PysToken(
                    TOKENS['NOTIN'],
                    self.current_token.position,
                    '{} {}'.format(KEYWORDS['not'], KEYWORDS['in'])
                )

            last_token = self.current_token

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            if (
                is_member and
                last_token.match(TOKENS['KEYWORD'], KEYWORDS['is']) and
                self.current_token.match(TOKENS['KEYWORD'], KEYWORDS['not'])
            ):
                operations[-1] = PysToken(
                    TOKENS['ISNOT'],
                    self.current_token.position,
                    '{} {}'.format(KEYWORDS['is'], KEYWORDS['not'])
                )

                result.register_advancement()
                self.advance()
                self.skip_expr(result)

            expr = result.register(func(), True)
            if result.error:
                return result

        if operations:
            expressions.append(expr)

        return result.success(PysChainOperatorNode(operations, expressions) if operations else expr)

    def binary_operator(self, func, operators, is_bitwise=False):
        result = PysParserResult()

        left = result.register(func())
        if result.error:
            return result

        while self.current_token.type in operators or (self.current_token.type, self.current_token.value) in operators:
            operand = (
                PysToken(TOKENS['XOR'], self.current_token.position, 'reversed')
                    if is_bitwise and self.future & REVERSE_POW_XOR and self.current_token.type == TOKENS['POW'] else
                self.current_token
            )

            result.register_advancement()
            self.advance()
            self.skip_expr(result)

            right = result.register(func(), True)
            if result.error:
                return result

            left = PysBinaryOperatorNode(left, operand, right)

        return result.success(left)

    def close_parenthesis(self, result, left_parenthesis_token):
        if self.current_token.type != parenthesises_map[left_parenthesis_token.type]:

            if self.current_token.type in parenthesises_map.values():
                return result.failure(
                    self.error(
                        "closing parenthesis {!r} does not match opening parenthesis {!r}".format(
                            chr(self.current_token.type),
                            chr(left_parenthesis_token.type)
                        )
                    )
                )

            elif self.current_token.type == TOKENS['EOF']:
                return result.failure(
                    self.error(
                        "{!r} was never closed".format(chr(left_parenthesis_token.type)),
                        left_parenthesis_token.position
                    )
                )

            else:
                return result.failure(self.error("invalid syntax"))

        result.register_advancement()
        self.advance()

    def skip(self, result, types=TOKENS['NEWLINE']):
        if not isinstance(types, tuple):
            types = (types,)

        count = 0

        while self.current_token.type in types:
            result.register_advancement()
            self.advance()
            count += 1

        return count

    def skip_expr(self, result):
        if self.parenthesis_level > 0:
            return self.skip(result)

        return 0

    def proccess_future(self, name):
        result = PysParserResult()

        if name == 'braces':
            return result.failure(self.error("yes, i use it for this language"))

        elif name == 'indent':
            return result.failure(self.error("not a chance"))

        elif name == 'reverse_pow_xor':
            self.future |= REVERSE_POW_XOR
            return result.success(False)

        return result.failure(self.error("future feature {} is not defined".format(name)))