from enum import Enum
from language.utils import Position


# ===========================
# KEYWORDS
# ===========================
class Keyword(Enum):
    ASSIGN_START = 'soch'
    ASSIGN_END = 'hai'
    AND = 'aur'
    OR = 'ya'
    NOT = 'ulta'


# ===========================
# TOKEN TYPES
# ===========================
class TokenType(Enum):
    EOF = '__EOF__'

    INT = 'INT'
    FLOAT = 'FLOAT'

    PLUS = '+'
    MINUS = '-'
    MULTIPLY = '*'
    DIVIDE = '/'
    POWER = '^'

    L_PAREN = '('
    R_PAREN = ')'

    IDENTIFIER = 'ID'
    KEYWORD = 'KEYWORD'

    GREATER_THAN = '>'
    LESS_THAN = '<'
    GREATER_THAN_EQUAL = '>='
    LESS_THAN_EQUAL = '<='


# ===========================
# TOKEN CLASS
# ===========================
class Token:
    def __init__(self, token_type: TokenType, value=None, pos_start: Position = None, pos_end: Position = None):
        self.token_type = token_type
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.increment()

        if pos_end:
            self.pos_end = pos_end.copy()

    def __repr__(self):
        if self.value: return f'{self.token_type.name}({self.value})'
        return self.token_type.name


# ===========================
# SYMBOL TABLE
# ===========================
class SymbolTable:
    def __init__(self):
        self.symbols = {}
        self.parent = None

    def get(self, variable):
        value = self.symbols.get(variable)
        if value is not None and self.parent:
            return self.parent.get(variable)
        return value

    def set(self, variable, value):
        self.symbols[variable] = value

    def remove(self, variable):
        del self.symbols[variable]
