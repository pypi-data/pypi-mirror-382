from .bases import Pys
from .constants import TOKENS, KEYWORDS, DEFAULT, OPTIMIZE
from .context import PysContext
from .exceptions import PysException
from .handlers import handle_call, handle_exception
from .nodes import PysSequenceNode, PysIdentifierNode, PysAttributeNode, PysSubscriptNode
from .objects import PysFunction
from .pysbuiltins import require, pyimport, ce, nce, increment, decrement
from .results import PysRunTimeResult
from .singletons import undefined
from .symtab import PysClassSymbolTable
from .utils import inplace_functions_map, keyword_identifiers_map, is_object_of, Iterable

class PysInterpreter(Pys):

    def __init__(self, flags=DEFAULT):
        self.flags = flags

    def visit(self, node, context):
        return getattr(self, 'visit_' + type(node).__name__[3:])(node, context)

    def visit_NumberNode(self, node, context):
        return PysRunTimeResult().success(node.token.value)

    def visit_StringNode(self, node, context):
        return PysRunTimeResult().success(node.token.value)

    def visit_SequenceNode(self, node, context):
        result = PysRunTimeResult()
        elements = []

        if node.type == 'dict':

            for key, value in node.elements:
                key = result.register(self.visit(key, context))
                if result.should_return():
                    return result

                value = result.register(self.visit(value, context))
                if result.should_return():
                    return result

                elements.append((key, value))

        else:

            for element in node.elements:
                elements.append(result.register(self.visit(element, context)))
                if result.should_return():
                    return result

        with handle_exception(result, context, node.position):
            if node.type == 'tuple':
                elements = tuple(elements)
            elif node.type == 'dict':
                elements = dict(elements)
            elif node.type == 'set':
                elements = set(elements)

        if result.should_return():
            return result

        return result.success(elements)

    def visit_IdentifierNode(self, node, context):
        result = PysRunTimeResult()

        with handle_exception(result, context, node.position):
            value = context.symbol_table.get(node.token.value)

            if value is undefined:
                closest_symbol = context.symbol_table.find_closest(node.token.value)

                return result.failure(
                    PysException(
                        NameError(
                            "{!r} is not defined{}".format(
                                node.token.value,
                                '' if closest_symbol is None else ". Did you mean {!r}?".format(closest_symbol)
                            )
                        ),
                        context,
                        node.position
                    )
                )

        if result.should_return():
            return result

        return result.success(value)

    def visit_KeywordNode(self, node, context):
        return PysRunTimeResult().success(keyword_identifiers_map[node.token.value])

    def visit_AttributeNode(self, node, context):
        result = PysRunTimeResult()

        object = result.register(self.visit(node.object, context))
        if result.should_return():
            return result

        with handle_exception(result, context, node.attribute.position):
            value = getattr(object, node.attribute.value)

        if result.should_return():
            return result

        return result.success(value)

    def visit_SubscriptNode(self, node, context):
        result = PysRunTimeResult()

        object = result.register(self.visit(node.object, context))
        if result.should_return():
            return result

        slice = result.register(self.visit_slice_from_SubscriptNode(node.slice, context))
        if result.should_return():
            return result

        with handle_exception(result, context, node.position):
            value = object[slice]

        if result.should_return():
            return result

        return result.success(value)

    def visit_AssignNode(self, node, context):
        result = PysRunTimeResult()

        value = result.register(self.visit(node.value, context))
        if result.should_return():
            return result

        result.register(self.visit_unpack_AssignNode(node.target, context, value, node.operand.type))
        if result.should_return():
            return result

        return result.success(value)

    def visit_ChainOperatorNode(self, node, context):
        result = PysRunTimeResult()

        left = result.register(self.visit(node.expressions[0], context))
        if result.should_return():
            return result

        with handle_exception(result, context, node.position):
            value = True

            for i, operand in enumerate(node.operations):
                right = result.register(self.visit(node.expressions[i + 1], context))
                if result.should_return():
                    return result

                if operand.match(TOKENS['KEYWORD'], KEYWORDS['in']):
                    comparison = left in right
                elif operand.match(TOKENS['KEYWORD'], KEYWORDS['is']):
                    comparison = left is right
                elif operand.type == TOKENS['NOTIN']:
                    comparison = left not in right
                elif operand.type == TOKENS['ISNOT']:
                    comparison = left is not right
                elif operand.type == TOKENS['EE']:
                    comparison = left == right
                elif operand.type == TOKENS['NE']:
                    comparison = left != right
                elif operand.type == TOKENS['CE']:
                    comparison = ce(left, right)
                elif operand.type == TOKENS['NCE']:
                    comparison = nce(left, right)
                elif operand.type == TOKENS['LT']:
                    comparison = left < right
                elif operand.type == TOKENS['GT']:
                    comparison = left > right
                elif operand.type == TOKENS['LTE']:
                    comparison = left <= right
                elif operand.type == TOKENS['GTE']:
                    comparison = left >= right

                if not comparison:
                    value = False
                    break

                left = right

        if result.should_return():
            return result

        return result.success(value)

    def visit_TernaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        condition = result.register(self.visit(node.condition, context))
        if result.should_return():
            return result

        if condition:
            value = result.register(self.visit(node.valid, context))
            if result.should_return():
                return result

        else:
            value = result.register(self.visit(node.invalid, context))
            if result.should_return():
                return result

        return result.success(value)

    def visit_BinaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        left = result.register(self.visit(node.left, context))
        if result.should_return():
            return result

        if node.operand.match(TOKENS['KEYWORD'], KEYWORDS['and']):
            if left:
                right = result.register(self.visit(node.right, context))
                if result.should_return():
                    return result

                return result.success(right)

            return result.success(left)

        elif node.operand.match(TOKENS['KEYWORD'], KEYWORDS['or']):
            if not left:
                right = result.register(self.visit(node.right, context))
                if result.should_return():
                    return result

                return result.success(right)

            return result.success(left)

        elif node.operand.type == TOKENS['NULLISH']:
            if left is None:
                right = result.register(self.visit(node.right, context))
                if result.should_return():
                    return result

                return result.success(right)

            return result.success(left)

        else:
            right = result.register(self.visit(node.right, context))
            if result.should_return():
                return result

        with handle_exception(result, context, node.position):

            if node.operand.type == TOKENS['PLUS']:
                value = left + right
            elif node.operand.type == TOKENS['MINUS']:
                value = left - right
            elif node.operand.type == TOKENS['MUL']:
                value = left * right
            elif node.operand.type == TOKENS['DIV']:
                value = left / right
            elif node.operand.type == TOKENS['FDIV']:
                value = left // right
            elif node.operand.type == TOKENS['MOD']:
                value = left % right
            elif node.operand.type == TOKENS['AT']:
                value = left @ right
            elif node.operand.type == TOKENS['POW']:
                value = left ** right
            elif node.operand.type == TOKENS['AND']:
                value = left & right
            elif node.operand.type == TOKENS['OR']:
                value = left | right
            elif node.operand.type == TOKENS['XOR']:
                value = left ^ right
            elif node.operand.type == TOKENS['LSHIFT']:
                value = left << right
            elif node.operand.type == TOKENS['RSHIFT']:
                value = left >> right

        if result.should_return():
            return result

        return result.success(value)

    def visit_UnaryOperatorNode(self, node, context):
        result = PysRunTimeResult()

        value = result.register(self.visit(node.value, context))
        if result.should_return():
            return result

        with handle_exception(result, context, node.position):

            if node.operand.match(TOKENS['KEYWORD'], KEYWORDS['not']):
                new_value = not value
            elif node.operand.type == TOKENS['PLUS']:
                new_value = +value
            elif node.operand.type == TOKENS['MINUS']:
                new_value = -value
            elif node.operand.type == TOKENS['NOT']:
                new_value = ~value

            elif node.operand.type in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
                new_value = value

                value = increment(value) if node.operand.type == TOKENS['INCREMENT'] else decrement(value)

                result.register(self.visit_unpack_AssignNode(node.value, context, value))
                if result.should_return():
                    return result

                if node.operand_position == 'left':
                    new_value = value

        if result.should_return():
            return result

        return result.success(new_value)

    def visit_ImportNode(self, node, context):
        result = PysRunTimeResult()

        name, as_name = node.name

        with handle_exception(result, context, name.position):
            handle_call(require, context, name.position, self.flags)

            try:
                module = require(name.value)
            except ModuleNotFoundError:
                module = pyimport(name.value)

        if result.should_return():
            return result

        if node.packages == 'all':
            all_packages = getattr(
                module, '__all__',
                (package for package in dir(module) if not package.startswith('_'))
            )

            with handle_exception(result, context, name.position):
                for package in all_packages:
                    context.symbol_table.set(package, getattr(module, package))

            if result.should_return():
                return result

        elif node.packages:

            for package, as_package in node.packages:

                with handle_exception(result, context, package.position):
                    context.symbol_table.set(
                        (package if as_package is None else as_package).value,
                        getattr(module, package.value)
                    )

                if result.should_return():
                    return result

        elif not (name.type == TOKENS['STRING'] and as_name is None):
            context.symbol_table.set(
                (name if as_name is None else as_name).value,
                module
            )

        return result.success(None)

    def visit_IfNode(self, node, context):
        result = PysRunTimeResult()

        for condition, body in node.cases_body:
            condition_value = result.register(self.visit(condition, context))
            if result.should_return():
                return result

            if condition_value:
                result.register(self.visit(body, context))
                if result.should_return():
                    return result

                return result.success(None)

        if node.else_body:
            result.register(self.visit(node.else_body, context))
            if result.should_return():
                return result

        return result.success(None)

    def visit_SwitchNode(self, node, context):
        result = PysRunTimeResult()

        target = result.register(self.visit(node.target, context))
        if result.should_return():
            return result

        fall_through = False

        for condition, body in node.cases_body:
            case = result.register(self.visit(condition, context))
            if result.should_return():
                return result

            if fall_through or target == case:
                result.register(self.visit(body, context))
                if result.should_return() and not result.loop_should_break:
                    return result

                if result.loop_should_break:
                    result.loop_should_break = False
                    fall_through = False
                else:
                    fall_through = True

        if fall_through and node.default_body:
            result.register(self.visit(node.default_body, context))
            if result.should_return() and not result.loop_should_break:
                return result

            if result.loop_should_break:
                result.loop_should_break = False

        return result.success(None)

    def visit_TryNode(self, node, context):
        result = PysRunTimeResult()

        result.register(self.visit(node.body, context))

        if node.catch_body and result.error:
            if node.error_variable:
                context.symbol_table.set(node.error_variable.value, result.error.exception)

            result.error = None
            result.register(self.visit(node.catch_body, context))

        if node.finally_body:
            finally_result = PysRunTimeResult()

            finally_result.register(self.visit(node.finally_body, context))
            if finally_result.should_return():
                return finally_result

        if result.should_return():
            return result

        return result.success(None)

    def visit_ForNode(self, node, context):
        result = PysRunTimeResult()

        target = node.init[0]

        if len(node.init) == 2:
            iterator = node.init[1]

            iter_object = result.register(self.visit(iterator, context))
            if result.should_return():
                return result

            with handle_exception(result, context, iterator.position):
                iter_object = iter(iter_object)

            if result.should_return():
                return result

            def condition():
                with handle_exception(result, context, target.position):
                    result.register(self.visit_unpack_AssignNode(target, context, next(iter_object)))

                if result.should_return():
                    if is_object_of(result.error.exception, StopIteration):
                        result.error = None
                    return False

                return True

            def update():
                pass

        elif len(node.init) == 3:
            conditor = node.init[1]
            updater = node.init[2]

            if target:
                result.register(self.visit(target, context))
                if result.should_return():
                    return result

            if conditor:
                def condition():
                    value = result.register(self.visit(conditor, context))
                    if result.should_return():
                        return False
                    return value
            else:
                def condition():
                    return True

            if updater:
                def update():
                    result.register(self.visit(updater, context))
            else:
                def update():
                    pass

        while True:
            done = condition()
            if result.should_return():
                return result

            if not done:
                break

            if node.body:
                result.register(self.visit(node.body, context))
                if result.should_return() and not result.loop_should_continue and not result.loop_should_break:
                    return result

                if result.loop_should_continue:
                    result.loop_should_continue = False

                elif result.loop_should_break:
                    break

            update()
            if result.should_return():
                return result

        if result.loop_should_break:
            result.loop_should_break = False

        elif node.else_body:
            result.register(self.visit(node.else_body, context))
            if result.should_return():
                return result

        return result.success(None)

    def visit_WhileNode(self, node, context):
        result = PysRunTimeResult()

        while True:
            condition = result.register(self.visit(node.condition, context))
            if result.should_return():
                return result

            if not condition:
                break

            if node.body:
                result.register(self.visit(node.body, context))
                if result.should_return() and not result.loop_should_continue and not result.loop_should_break:
                    return result

                if result.loop_should_continue:
                    result.loop_should_continue = False

                elif result.loop_should_break:
                    break

        if result.loop_should_break:
            result.loop_should_break = False

        elif node.else_body:
            result.register(self.visit(node.else_body, context))
            if result.should_return():
                return result

        return result.success(None)

    def visit_DoWhileNode(self, node, context):
        result = PysRunTimeResult()

        while True:
            if node.body:
                result.register(self.visit(node.body, context))
                if result.should_return() and not result.loop_should_continue and not result.loop_should_break:
                    return result

                if result.loop_should_continue:
                    result.loop_should_continue = False

                elif result.loop_should_break:
                    break

            condition = result.register(self.visit(node.condition, context))
            if result.should_return():
                return result

            if not condition:
                break

        if result.loop_should_break:
            result.loop_should_break = False

        elif node.else_body:
            result.register(self.visit(node.else_body, context))
            if result.should_return():
                return result

        return result.success(None)

    def visit_ClassNode(self, node, context):
        result = PysRunTimeResult()

        bases = []

        for base in node.bases:
            bases.append(result.register(self.visit(base, context)))
            if result.should_return():
                return result

        class_context = PysContext(
            name=node.name.value,
            file=context.file,
            symbol_table=PysClassSymbolTable(context.symbol_table),
            parent=context,
            parent_entry_position=node.position
        )

        result.register(self.visit(node.body, class_context))
        if result.should_return():
            return result

        with handle_exception(result, context, node.position):
            cls = type(node.name.value, tuple(bases), class_context.symbol_table.symbols)

        if result.should_return():
            return result

        for decorator in reversed(node.decorators):
            decorator_func = result.register(self.visit(decorator, context))
            if result.should_return():
                return result

            with handle_exception(result, context, decorator.position):
                cls = decorator_func(cls)

            if result.should_return():
                return result

        context.symbol_table.set(node.name.value, cls)

        return result.success(None)

    def visit_FunctionNode(self, node, context):
        result = PysRunTimeResult()

        parameters = []

        for parameter in node.parameters:

            if isinstance(parameter, tuple):
                value = result.register(self.visit(parameter[1], context))
                if result.should_return():
                    return result

                parameters.append((parameter[0].value, value))

            else:
                parameters.append(parameter.value)

        func = PysFunction(
            name=None if node.name is None else node.name.value,
            parameters=parameters,
            body=node.body,
            position=node.position,
            context=context
        )

        for decorator in reversed(node.decorators):
            decorator_func = result.register(self.visit(decorator, context))
            if result.should_return():
                return result

            with handle_exception(result, context, decorator.position):
                func = decorator_func(func)

            if result.should_return():
                return result

        if node.name is not None:
            context.symbol_table.set(node.name.value, func)

        return result.success(func)

    def visit_CallNode(self, node, context):
        result = PysRunTimeResult()

        name = result.register(self.visit(node.name, context))
        if result.should_return():
            return result

        args = []
        kwargs = {}

        for arg in node.args:

            if isinstance(arg, tuple):
                kwargs[arg[0].value] = result.register(self.visit(arg[1], context))
                if result.should_return():
                    return result

            else:
                args.append(result.register(self.visit(arg, context)))
                if result.should_return():
                    return result

        with handle_exception(result, context, node.position):
            handle_call(name, context, node.position, self.flags)
            value = name(*args, **kwargs)

        if result.should_return():
            return result

        return result.success(value)

    def visit_ReturnNode(self, node, context):
        result = PysRunTimeResult()

        if node.value:
            value = result.register(self.visit(node.value, context))
            if result.should_return():
                return result

            return result.success_return(value)

        return result.success_return(None)

    def visit_DeleteNode(self, node, context):
        result = PysRunTimeResult()

        for target in node.targets:

            if isinstance(target, PysIdentifierNode):

                with handle_exception(result, context, target.position):
                    success = context.symbol_table.remove(target.token.value)

                    if not success:
                        closest_symbol = context.symbol_table.find_closest(target.token.value)

                        result.failure(
                            PysException(
                                NameError(
                                    "{!r} is not defined{}".format(
                                        target.token.value,
                                        '' if closest_symbol is None else ". Did you mean {!r}?".format(closest_symbol)
                                    )
                                    if context.symbol_table.get(target.token.value) is undefined else
                                    "{!r} is not defined on local".format(target.token.value)
                                ),
                                context,
                                target.position
                            )
                        )

                if result.should_return():
                    return result

            elif isinstance(target, PysSubscriptNode):
                object = result.register(self.visit(target.object, context))
                if result.should_return():
                    return result

                slice = result.register(self.visit_slice_from_SubscriptNode(target.slice, context))
                if result.should_return():
                    return result

                with handle_exception(result, context, target.position):
                    del object[slice]

                if result.should_return():
                    return result

            elif isinstance(target, PysAttributeNode):
                object = result.register(self.visit(target.object, context))
                if result.should_return():
                    return result

                with handle_exception(result, context, target.position):
                    delattr(object, target.attribute.value)

                if result.should_return():
                    return result

        return result.success(None)

    def visit_ThrowNode(self, node, context):
        result = PysRunTimeResult()

        target = result.register(self.visit(node.target, context))
        if result.should_return():
            return result

        if not is_object_of(target, BaseException):
            return result.failure(
                PysException(
                    TypeError("exceptions must derive from BaseException"),
                    context,
                    node.target.position
                )
            )

        return result.failure(PysException(target, context, node.position))

    def visit_AssertNode(self, node, context):
        result = PysRunTimeResult()

        if not (self.flags & OPTIMIZE):
            condition = result.register(self.visit(node.condition, context))
            if result.should_return():
                return result

            if not condition:

                if node.message:
                    message = result.register(self.visit(node.message, context))
                    if result.should_return():
                        return result

                    return result.failure(PysException(AssertionError(message), context, node.position))

                return result.failure(PysException(AssertionError, context, node.position))

        return result.success(None)

    def visit_EllipsisNode(self, node, context):
        return PysRunTimeResult().success(Ellipsis)

    def visit_ContinueNode(self, node, context):
        return PysRunTimeResult().success_continue()

    def visit_BreakNode(self, node, context):
        return PysRunTimeResult().success_break()

    def visit_slice_from_SubscriptNode(self, node, context):
        result = PysRunTimeResult()

        if isinstance(node, list):
            slices = []

            for element in node:
                slices.append(result.register(self.visit_slice_from_SubscriptNode(element, context)))
                if result.should_return():
                    return result

            return result.success(tuple(slices))

        elif isinstance(node, tuple):
            start, stop, step = node

            if start is not None:
                start = result.register(self.visit(start, context))
                if result.should_return():
                    return result

            if stop is not None:
                stop = result.register(self.visit(stop, context))
                if result.should_return():
                    return result

            if step is not None:
                step = result.register(self.visit(step, context))
                if result.should_return():
                    return result

            return result.success(slice(start, stop, step))

        else:
            value = result.register(self.visit(node, context))
            if result.should_return():
                return result

            return result.success(value)

    def visit_unpack_AssignNode(self, node, context, value, operand=TOKENS['EQ']):
        result = PysRunTimeResult()

        if isinstance(node, PysSequenceNode):

            if not isinstance(value, Iterable):
                return result.failure(
                    PysException(
                        TypeError("cannot unpack non-iterable"),
                        context,
                        node.position
                    )
                )

            count = 0

            with handle_exception(result, context, node.position):

                for i, element in enumerate(value):

                    if i < len(node.elements):
                        result.register(self.visit_unpack_AssignNode(node.elements[i], context, element, operand))
                        if result.should_return():
                            return result

                        count += 1

                    else:
                        result.failure(
                            PysException(
                                ValueError("to many values to unpack (expected {})".format(len(node.elements))),
                                context,
                                node.position
                            )
                        )

                        break

            if result.should_return():
                return result

            if count < len(node.elements):
                return result.failure(
                    PysException(
                        ValueError(
                            "not enough values to unpack (expected {}, got {})".format(len(node.elements), count)
                        ),
                        context,
                        node.position
                    )
                )

        elif isinstance(node, PysSubscriptNode):
            object = result.register(self.visit(node.object, context))
            if result.should_return():
                return result

            slice = result.register(self.visit_slice_from_SubscriptNode(node.slice, context))
            if result.should_return():
                return result

            with handle_exception(result, context, node.position):
                if operand == TOKENS['EQ']:
                    object[slice] = value
                else:
                    object[slice] = inplace_functions_map[operand](object[slice], value)

            if result.should_return():
                return result

        elif isinstance(node, PysAttributeNode):
            object = result.register(self.visit(node.object, context))
            if result.should_return():
                return result

            with handle_exception(result, context, node.position):
                if operand == TOKENS['EQ']:
                    setattr(object, node.attribute.value, value)
                else:
                    setattr(
                        object,
                        node.attribute.value,
                        inplace_functions_map[operand](getattr(object, node.attribute.value), value)
                    )

            if result.should_return():
                return result

        elif isinstance(node, PysIdentifierNode):

            with handle_exception(result, context, node.position):
                success = context.symbol_table.set(node.token.value, value, operand)

                if not success:
                    closest_symbol = context.symbol_table.find_closest(node.token.value)

                    result.failure(
                        PysException(
                            NameError(
                                "{!r} is not defined{}".format(
                                    node.token.value,
                                    '' if closest_symbol is None else ". Did you mean {!r}?".format(closest_symbol)
                                )
                            ),
                            context,
                            node.position
                        )
                    )

            if result.should_return():
                return result

        return result.success(None)