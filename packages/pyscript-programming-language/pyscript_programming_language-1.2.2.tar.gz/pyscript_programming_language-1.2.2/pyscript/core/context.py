from .bases import Pys

class PysContext(Pys):

    def __init__(self, name, file, symbol_table=None, parent=None, parent_entry_position=None):
        self.name = name
        self.file = file
        self.symbol_table = symbol_table
        self.parent = parent
        self.parent_entry_position = parent_entry_position

    def __repr__(self):
        return '<Context {!r}>'.format(self.name)