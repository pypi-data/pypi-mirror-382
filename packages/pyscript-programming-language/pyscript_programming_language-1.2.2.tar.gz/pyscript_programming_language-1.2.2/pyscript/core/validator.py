from .bases import Pys
from .constants import TOKENS
from .context import PysContext
from .exceptions import PysException
from .nodes import PysSequenceNode, PysIdentifierNode, PysAttributeNode, PysSubscriptNode

class PysValidator(Pys):

    def __init__(self, file, context_parent=None, context_parent_entry_position=None):
        self.file = file
        self.context = context_parent
        self.context_parent_entry_position = context_parent_entry_position

        self.in_loop = 0
        self.in_function = 0
        self.in_switch = 0

        self.error = None

    def throw(self, message, position):
        if self.error is None:
            self.error = PysException(
                SyntaxError(message),
                PysContext(
                    name=None,
                    file=self.file,
                    parent=self.context,
                    parent_entry_position=self.context_parent_entry_position
                ),
                position
            )

    def visit(self, node):
        func = getattr(self, 'visit_' + type(node).__name__[3:], None)

        if not self.error and func:
            func(node)

        return self.error

    def visit_SequenceNode(self, node):
        if node.type == 'dict':
            for key, value in node.elements:
                self.visit(key)
                if self.error:
                    return

                self.visit(value)
                if self.error:
                    return

        else:
            for element in node.elements:
                self.visit(element)
                if self.error:
                    return

    def visit_SubscriptNode(self, node):
        self.visit(node.object)
        if self.error:
            return

        self.check_valid_slice_from_SubscriptNode(node.slice)

    def visit_AttributeNode(self, node):
        self.visit(node.object)

    def visit_AssignNode(self, node):
        self.check_valid_AssignNode(
            node.target,
            "cannot assign to expression here. Maybe you meant '==' instead of '='?"
        )

        if self.error:
            return

        self.visit(node.value)

    def visit_ChainOperatorNode(self, node):
        for expression in node.expressions:
            self.visit(expression)
            if self.error:
                return

    def visit_TernaryOperatorNode(self, node):
        self.visit(node.condition)
        if self.error:
            return

        self.visit(node.valid)
        if self.error:
            return

        self.visit(node.invalid)

    def visit_BinaryOperatorNode(self, node):
        self.visit(node.left)
        if self.error:
            return

        self.visit(node.right)

    def visit_UnaryOperatorNode(self, node):
        if node.operand.type in (TOKENS['INCREMENT'], TOKENS['DECREMENT']):
            if not isinstance(node.value, (PysIdentifierNode, PysAttributeNode, PysSubscriptNode)):
                self.throw(
                    "cannot {} literal".format('increase' if node.operand.type == TOKENS['INCREMENT'] else 'decrease'),
                    node.position
                )
                return

        self.visit(node.value)

    def visit_IfNode(self, node):
        for condition, body in node.cases_body:
            self.visit(condition)
            if self.error:
                return

            self.visit(body)
            if self.error:
                return

        if node.else_body:
            self.visit(node.else_body)

    def visit_SwitchNode(self, node):
        self.visit(node.target)
        if self.error:
            return

        self.in_switch += 1

        for condition, body in node.cases_body:
            self.visit(condition)
            if self.error:
                return

            self.visit(body)
            if self.error:
                return

        if node.default_body:
            self.visit(node.default_body)
            if self.error:
                return

        self.in_switch -= 1

    def visit_TryNode(self, node):
        self.visit(node.body)
        if self.error:
            return

        if node.catch_body:
            self.visit(node.catch_body)
            if self.error:
                return

        if node.finally_body:
            self.visit(node.finally_body)

    def visit_ForNode(self, node):
        if len(node.init) == 2:
            self.check_valid_AssignNode(node.init[0], "cannot assign to expression")
            if self.error:
                return

            self.visit(node.init[1])
            if self.error:
                return

        elif len(node.init) == 3:
            for element in node.init:
                self.visit(element)
                if self.error:
                    return

        if node.body:
            self.in_loop += 1

            self.visit(node.body)
            if self.error:
                return

            self.in_loop -= 1

        if node.else_body:
            self.visit(node.else_body)

    def visit_WhileNode(self, node):
        self.visit(node.condition)
        if self.error:
            return

        if node.body:
            self.in_loop += 1

            self.visit(node.body)
            if self.error:
                return

            self.in_loop -= 1

        if node.else_body:
            self.visit(node.else_body)

    def visit_DoWhileNode(self, node):
        if node.body:
            self.in_loop += 1

            self.visit(node.body)
            if self.error:
                return

            self.in_loop -= 1

        self.visit(node.condition)
        if self.error:
            return

        if node.else_body:
            self.visit(node.else_body)

    def visit_ClassNode(self, node):
        for decorator in node.decorators:
            self.visit(decorator)
            if self.error:
                return

        for base in node.bases:
            self.visit(base)
            if self.error:
                return

        in_loop, in_function, in_switch = self.in_loop, self.in_function, self.in_switch

        self.in_loop = 0
        self.in_function = 0
        self.in_switch = 0

        self.visit(node.body)
        if self.error:
            return

        self.in_loop = in_loop
        self.in_function = in_function
        self.in_switch = in_switch

    def visit_FunctionNode(self, node):
        for decorator in node.decorators:
            self.visit(decorator)
            if self.error:
                return

        names = set()

        for element in node.parameters:
            token = (element[0] if isinstance(element, tuple) else element)
            name = token.value

            if name in names:
                return self.throw("duplicate argument {!r} in function definition".format(name), token.position)

            names.add(name)

            if isinstance(element, tuple):
                self.visit(element[1])
                if self.error:
                    return

        in_loop, in_function, in_switch = self.in_loop, self.in_function, self.in_switch

        self.in_loop = 0
        self.in_function = 1
        self.in_switch = 0

        self.visit(node.body)
        if self.error:
            return

        self.in_loop = in_loop
        self.in_function = in_function
        self.in_switch = in_switch

    def visit_CallNode(self, node):
        self.visit(node.name)
        if self.error:
            return

        names = set()

        for element in node.args:
            value = element

            if isinstance(element, tuple):
                token, value = element
                name = token.value

                if name in names:
                    self.throw("duplicate argument {!r} in call definition".format(name), token.position)
                    return

                names.add(name)

            self.visit(value)
            if self.error:
                return

    def visit_ReturnNode(self, node):
        if self.in_function == 0:
            self.throw("return outside of function", node.position)
            return

        if node.value:
            self.visit(node.value)

    def visit_DeleteNode(self, node):
        for element in node.targets:

            if isinstance(element, PysSubscriptNode):
                self.visit(element.object)
                if self.error:
                    return

                self.check_valid_slice_from_SubscriptNode(element.slice)
                if self.error:
                    return

            elif isinstance(element, PysAttributeNode):
                self.visit(element.object)
                if self.error:
                    return

            elif not isinstance(element, PysIdentifierNode):
                self.throw("cannot delete literal", element.position)
                return

    def visit_ThrowNode(self, node):
        self.visit(node.target)

    def visit_AssertNode(self, node):
        self.visit(node.condition)
        if self.error:
            return

        if node.message:
            self.visit(node.message)

    def visit_ContinueNode(self, node):
        if self.in_loop == 0:
            self.throw("continue outside of loop", node.position)

    def visit_BreakNode(self, node):
        if self.in_loop == 0 and self.in_switch == 0:
            self.throw("break outside of loop or switch case", node.position)

    def check_valid_slice_from_SubscriptNode(self, slice):
        if isinstance(slice, list):
            for element in slice:
                self.check_valid_slice_from_SubscriptNode(element)
                if self.error:
                    return

        elif isinstance(slice, tuple):
            for element in slice:
                self.visit(element)
                if self.error:
                    return

        else:
            self.visit(slice)

    def check_valid_AssignNode(self, node, message):
        if isinstance(node, PysSequenceNode):
            for element in node.elements:
                self.check_valid_AssignNode(element, message)
                if self.error:
                    return

        elif isinstance(node, PysSubscriptNode):
            self.visit(node.object)
            if self.error:
                return

            self.check_valid_slice_from_SubscriptNode(node.slice)

        elif isinstance(node, PysAttributeNode):
            self.visit(node.object)

        elif not isinstance(node, PysIdentifierNode):
            self.throw(message, node.position)