from .bases import Pys
from .utils import to_str

from io import IOBase

class PysBuffer(Pys):
    pass

class PysFileBuffer(PysBuffer):

    def __init__(self, text, name=None):
        if isinstance(text, PysFileBuffer):
            self.text = to_str(text.text)
            self.name = to_str(text.name if name is None else name)

        elif isinstance(text, IOBase):
            self.text = to_str(text)
            self.name = to_str(text.name if name is None else name)

        else:
            self.text = to_str(text)
            self.name = '<string>' if name is None else to_str(name)

    def __repr__(self):
        return '<FileBuffer from {!r}>'.format(self.name)

class PysCode(PysBuffer):

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)