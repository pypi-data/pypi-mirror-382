from .bases import Pys
from .position import PysPosition

class PysNode(Pys):
    pass

class PysNumberNode(PysNode):

    def __init__(self, token):
        self.position = token.position
        self.token = token

    def __repr__(self):
        return 'Number(value={!r})'.format(self.token.value)

class PysStringNode(PysNode):

    def __init__(self, token):
        self.position = token.position
        self.token = token

    def __repr__(self):
        return 'String(value={!r})'.format(self.token.value)

class PysSequenceNode(PysNode):

    def __init__(self, type, elements, position):
        self.position = position
        self.type = type
        self.elements = elements

    def __repr__(self):
        return 'Sequence(type={!r}, elements={!r})'.format(self.type, self.elements)

class PysIdentifierNode(PysNode):

    def __init__(self, token):
        self.position = token.position
        self.token = token

    def __repr__(self):
        return 'Identifier(name={!r})'.format(self.token.value)

class PysKeywordNode(PysNode):

    def __init__(self, token):
        self.position = token.position
        self.token = token

    def __repr__(self):
        return 'Keyword(name={!r})'.format(self.token.value)

class PysAttributeNode(PysNode):

    def __init__(self, object, attribute):
        self.position = PysPosition(object.position.file, object.position.start, attribute.position.end)
        self.object = object
        self.attribute = attribute

    def __repr__(self):
        return 'Attribute(object={!r}, attribute={!r})'.format(self.object, self.attribute)

class PysSubscriptNode(PysNode):

    def __init__(self, object, slice, position):
        self.position = position
        self.object = object
        self.slice = slice

    def __repr__(self):
        return 'Subscript(object={!r}, slice={!r})'.format(self.object, self.slice)

class PysAssignNode(PysNode):

    def __init__(self, target, operand, value):
        self.position = PysPosition(target.position.file, target.position.start, value.position.end)
        self.target = target
        self.operand = operand
        self.value = value

    def __repr__(self):
        return 'Assign(target={!r}, operand={!r}, value={!r})'.format(self.target, self.operand, self.value)

class PysChainOperatorNode(PysNode):

    def __init__(self, operations, expressions):
        self.position = PysPosition(
            expressions[0].position.file,
            expressions[0].position.start,
            expressions[-1].position.end
        )

        self.operations = operations
        self.expressions = expressions

    def __repr__(self):
        return 'ChainOperator(operations={!r}, expressions={!r})'.format(self.operations, self.expressions)

class PysTernaryOperatorNode(PysNode):

    def __init__(self, condition, valid, invalid):
        self.position = PysPosition(condition.position.file, condition.position.start, invalid.position.end)
        self.condition = condition
        self.valid = valid
        self.invalid = invalid

    def __repr__(self):
        return 'TernaryOperator(condition={!r}, valid={!r}, invalid={!r})'.format(
            self.condition, self.valid, self.invalid
        )

class PysBinaryOperatorNode(PysNode):

    def __init__(self, left, operand, right):
        self.position = PysPosition(left.position.file, left.position.start, right.position.end)
        self.left = left
        self.operand = operand
        self.right = right

    def __repr__(self):
        return 'BinaryOperator(left={!r}, operand={!r}, right={!r})'.format(self.left, self.operand, self.right)

class PysUnaryOperatorNode(PysNode):

    def __init__(self, operand, value, operand_position):
        self.position = (
            PysPosition(operand.position.file, operand.position.start, value.position.end)
            if operand_position == 'left' else
            PysPosition(operand.position.file, value.position.start, operand.position.end)
        )

        self.operand = operand
        self.value = value
        self.operand_position = operand_position

    def __repr__(self):
        return 'UnaryOperator(operand={!r}, value={!r}, operand_position={!r})'.format(
            self.operand, self.value, self.operand_position
        )

class PysImportNode(PysNode):

    def __init__(self, name, packages, position):
        self.position = position
        self.name = name
        self.packages = packages

    def __repr__(self):
        return 'Import(name={!r}, packages={!r})'.format(self.name, self.packages)

class PysIfNode(PysNode):

    def __init__(self, cases_body, else_body, position):
        self.position = position
        self.cases_body = cases_body
        self.else_body = else_body

    def __repr__(self):
        return 'If(cases_body={!r}, else_body={!r})'.format(self.cases_body, self.else_body)

class PysSwitchNode(PysNode):

    def __init__(self, target, cases_body, default_body, position):
        self.position = position
        self.target = target
        self.cases_body = cases_body
        self.default_body = default_body

    def __repr__(self):
        return 'Switch(target={!r}, cases_body={!r}, default_body={!r})'.format(
            self.target, self.cases_body, self.default_body
        )

class PysTryNode(PysNode):

    def __init__(self, body, error_variable, catch_body, finally_body, position):
        self.position = position
        self.body = body
        self.error_variable = error_variable
        self.catch_body = catch_body
        self.finally_body = finally_body

    def __repr__(self):
        return 'Try(body={!r}, error_variable={!r}, catch_body={!r}, finally_body={!r})'.format(
            self.body, self.error_variable, self.catch_body, self.finally_body
        )

class PysForNode(PysNode):

    def __init__(self, init, body, else_body, position):
        self.position = position
        self.init = init
        self.body = body
        self.else_body = else_body

    def __repr__(self):
        return 'For(init={!r}, body={!r}, else_body={!r})'.format(self.init, self.body, self.else_body)

class PysWhileNode(PysNode):

    def __init__(self, condition, body, else_body, position):
        self.position = position
        self.condition = condition
        self.body = body
        self.else_body = else_body

    def __repr__(self):
        return 'While(condition={!r}, body={!r}, else_body={!r})'.format(self.condition, self.body, self.else_body)

class PysDoWhileNode(PysNode):

    def __init__(self, body, condition, else_body, position):
        self.position = position
        self.body = body
        self.condition = condition
        self.else_body = else_body

    def __repr__(self):
        return 'DoWhile(body={!r}, condition={!r}, else_body={!r})'.format(self.body, self.condition, self.else_body)

class PysClassNode(PysNode):

    def __init__(self, name, bases, body, position):
        self.position = position
        self.decorators = []
        self.name = name
        self.bases = bases
        self.body = body

    def __repr__(self):
        return 'Class(decorators={!r}, name={!r}, bases={!r}, body={!r})'.format(
            self.decorators, self.name, self.bases, self.body
        )

class PysFunctionNode(PysNode):

    def __init__(self, name, parameters, body, position):
        self.position = position
        self.decorators = []
        self.name = name
        self.parameters = parameters
        self.body = body

    def __repr__(self):
        return 'Function(decorators={!r}, name={!r}, parameters={!r}, body={!r})'.format(
            self.decorators, self.name, self.parameters, self.body
        )

class PysCallNode(PysNode):

    def __init__(self, name, args, position):
        self.position = position
        self.name = name
        self.args = args

    def __repr__(self):
        return 'Call(name={!r}, args={!r})'.format(self.name, self.args)

class PysReturnNode(PysNode):

    def __init__(self, value, position):
        self.position = position
        self.value = value

    def __repr__(self):
        return 'Return(value={!r})'.format(self.value)

class PysDeleteNode(PysNode):

    def __init__(self, targets, position):
        self.position = position
        self.targets = targets

    def __repr__(self):
        return 'Delete(targets={!r})'.format(self.targets)

class PysThrowNode(PysNode):

    def __init__(self, target, position):
        self.position = PysPosition(position.file, position.start, target.position.end)
        self.target = target

    def __repr__(self):
        return 'Throw(target={!r})'.format(self.target)

class PysAssertNode(PysNode):

    def __init__(self, condition, message):
        self.position = condition.position
        self.condition = condition
        self.message = message

    def __repr__(self):
        return 'Assert(condition={!r}, message={!r})'.format(self.condition, self.message)

class PysEllipsisNode(PysNode):

    def __init__(self, position):
        self.position = position

    def __repr__(self):
        return 'Ellipsis()'

class PysContinueNode(PysNode):

    def __init__(self, position):
        self.position = position

    def __repr__(self):
        return 'Continue()'

class PysBreakNode(PysNode):

    def __init__(self, position):
        self.position = position

    def __repr__(self):
        return 'Break()'