from .bases import Pys
from .constants import TOKENS
from .utils import inplace_functions_map, get_similarity_ratio

class PysSymbolTable(Pys):

    def __init__(self, parent=None):
        self.parent = parent.parent if isinstance(parent, PysClassSymbolTable) else parent

        self.module = None
        self.symbols = {}

    def find_closest(self, name, cutoff=0.6):
        symbols = set(self.symbols.keys())

        parent = self.parent
        while parent:
            symbols.update(parent.symbols.keys())
            parent = parent.parent

        from .singletons import undefined

        builtins = self.symbols.get('__builtins__', undefined)
        if builtins is not undefined:
            symbols.update(dir(builtins))

        if not symbols:
            return None

        best_match = None
        best_score = 0.0

        for sym in symbols:
            score = get_similarity_ratio(name, sym)
            if score > best_score:
                best_score = score
                best_match = sym

        return best_match if best_score >= cutoff else None

    def get(self, name):
        from .singletons import undefined

        value = self.symbols.get(name, undefined)
        if value is undefined:
            if self.parent:
                return self.parent.get(name)

            builtins = self.symbols.get('__builtins__', undefined)
            if builtins is not undefined:
                return getattr(builtins, name, undefined)

        return value

    def set(self, name, value, operand=TOKENS['EQ']):
        if operand == TOKENS['EQ']:
            self.symbols[name] = value
            return True

        if name not in self.symbols:
            return False

        self.symbols[name] = inplace_functions_map[operand](self.symbols[name], value)
        return True

    def remove(self, name):
        if name not in self.symbols:
            return False

        del self.symbols[name]
        return True

class PysClassSymbolTable(PysSymbolTable):

    def __init__(self, parent):
        super().__init__(parent)