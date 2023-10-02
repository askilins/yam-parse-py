class TokenType:
    # Literals:
    NUMBER = 1
    TEXT = 2
    MULTILINE = 3
    BOOL = 4

    # Iterables:
    DICT_KEY = 5
    LIST_ENTRY = 6
    LIST_INNER = 7

    # Extended types:
    OBJECT = 8
    TAG = 9

    # Flow:
    INDENT = 10
    NEW_LINE = 11
    BAR = 12

    EOF = 0

    @classmethod
    def type_name(cls, t_type: int) -> str:
        for key, value in vars(cls).items():
            if value == t_type:
                return key

        raise LookupError


class Token:
    def __init__(self, t_type: TokenType, lexeme: str, literal: object, line: int):
        self.t_type = t_type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line

    def to_string(self):
        return f"{self.t_type} {self.lexeme} {self.literal}"

    def __repr__(self):
        return f"<Token type: {TokenType.type_name(self.t_type)}, lexeme: {self.lexeme}, literal: {self.literal}, line: {self.line}>"
