import os

# paths
PYSCRIPT_PATH = os.path.sep.join(__file__.split(os.path.sep)[:-2])
LIBRARY_PATH = os.path.join(PYSCRIPT_PATH, 'lib')

# tokens offset
DOUBLE = 0xFF
TRIPLE = 0xFF * 2
WITH_EQ = 0xFF * 3
SPECIAL = 0xFF * 4

# tokens
TOKENS = {
    'EOF': ord('\0'),
    'KEYWORD': 1,
    'IDENTIFIER': 2,
    'NUMBER': 3,
    'STRING': 4,
    'PLUS': ord('+'),
    'MINUS': ord('-'),
    'MUL': ord('*'),
    'DIV': ord('/'),
    'FDIV': ord('/') + DOUBLE,
    'MOD': ord('%'),
    'AT': ord('@'),
    'POW': ord('*') + DOUBLE,
    'AND': ord('&'),
    'OR': ord('|'),
    'XOR': ord('^'),
    'NOT': ord('~'),
    'LSHIFT': ord('<') + DOUBLE,
    'RSHIFT': ord('>') + DOUBLE,
    'INCREMENT': ord('+') + DOUBLE,
    'DECREMENT': ord('-') + DOUBLE,
    'LPAREN': ord('('),
    'RPAREN': ord(')'),
    'LSQUARE': ord('['),
    'RSQUARE': ord(']'),
    'LBRACE': ord('{'),
    'RBRACE': ord('}'),
    'EQ': ord('='),
    'EE': ord('=') + DOUBLE,
    'NE': ord('!') + WITH_EQ,
    'CE': ord('~') + WITH_EQ,
    'NCE': ord('~') + SPECIAL,
    'LT': ord('<'),
    'GT': ord('>'),
    'LTE': ord('<') + WITH_EQ,
    'GTE': ord('>') + WITH_EQ,
    'EPLUS': ord('+') + WITH_EQ,
    'EMINUS': ord('-') + WITH_EQ,
    'EMUL': ord('*') + WITH_EQ,
    'EDIV': ord('/') + WITH_EQ,
    'EFDIV': ord('/') + DOUBLE + WITH_EQ,
    'EMOD': ord('%') + WITH_EQ,
    'EAT': ord('@') + WITH_EQ,
    'EPOW': ord('*') + DOUBLE + WITH_EQ,
    'EAND': ord('&') + WITH_EQ,
    'EOR': ord('|') + WITH_EQ,
    'EXOR': ord('^') + WITH_EQ,
    'ELSHIFT': ord('<') + DOUBLE + WITH_EQ,
    'ERSHIFT': ord('>') + DOUBLE + WITH_EQ,
    'NULLISH': ord('?') + DOUBLE,
    'COLON': ord(':'),
    'COMMA': ord(','),
    'DOT': ord('.'),
    'QUESTION': ord('?'),
    'ELLIPSIS': ord('.') + TRIPLE,
    'SEMICOLON': ord(';'),
    'NEWLINE': ord('\n'),
    'COMMENT': ord('#'),
    'NOTIN': 5,
    'ISNOT': 6
}

# keywords
KEYWORDS = {
    'False': 'False',
    'None': 'None',
    'True': 'True',
    'and': 'and',
    'as': 'as',
    'assert': 'assert',
    'break': 'break',
    'case': 'case',
    'catch': 'catch',
    'class': 'class',
    'continue': 'continue',
    'default': 'default',
    'del': 'del',
    'do': 'do',
    'elif': 'elif',
    'else': 'else',
    'finally': 'finally',
    'for': 'for',
    'from': 'from',
    'func': 'func',
    'if': 'if',
    'import': 'import',
    'in': 'in',
    'is': 'is',
    'not': 'not',
    'of': 'of',
    'or': 'or',
    'return': 'return',
    'switch': 'switch',
    'throw': 'throw',
    'try': 'try',
    'while': 'while'
}

# default color highlight
HIGHLIGHT = {
    'default': '#D4D4D4',
    'keyword': '#C586C0',
    'keyword-identifier': '#307CD6',
    'identifier': '#8CDCFE',
    'identifier-const': '#2EA3FF',
    'identifier-call': '#DCDCAA',
    'identifier-class': '#4EC9B0',
    'number': '#B5CEA8',
    'string': '#CE9178',
    'parenthesis-unmatch': '#B51819',
    'parenthesis-0': '#FFD705',
    'parenthesis-1': '#D45DBA',
    'parenthesis-2': '#1A9FFF',
    'comment': '#549952'
}

# flags
DEFAULT = 0
OPTIMIZE = 1 << 1
SILENT = 1 << 2
RETRES = 1 << 3
REVERSE_POW_XOR = 1 << 25