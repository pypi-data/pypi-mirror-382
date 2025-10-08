from .bases import Pys

class PysPosition(Pys):

    def __init__(self, file, start, end):
        self.file = file
        self.start = start
        self.end = end

    def __repr__(self):
        return '<Position({!r}, {!r}) from {!r}>'.format(self.start, self.end, self.file.name)