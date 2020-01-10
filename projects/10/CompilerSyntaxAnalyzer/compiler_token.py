from enum import Enum


class TokenType(Enum):
    KEYWORD = 1
    SYMBOL = 2
    INTEGER = 3
    STRING = 4
    IDENTIFIER = 5


class Token:

    def __init__(self, val, token_type):
        self.val = val
        self.token_type = token_type
