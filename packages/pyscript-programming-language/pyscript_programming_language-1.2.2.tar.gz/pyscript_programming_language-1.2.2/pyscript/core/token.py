from .bases import Pys
from .constants import TOKENS

class PysToken(Pys):

    def __init__(self, type, position, value=None):
        self.type = type
        self.position = position
        self.value = value

    def __repr__(self):
        name = '<UNKNOWN>'

        for token_name, token_type in TOKENS.items():
            if token_type == self.type:
                name = token_name
                break

        return 'Token({}{})'.format(name, '' if self.value is None else ', value={!r}'.format(self.value))

    def match(self, type, value):
        return self.type == type and self.value == value

    def matches(self, type, values):
        return self.type == type and self.value in values