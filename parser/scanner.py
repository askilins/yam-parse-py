from .tokens import Token, TokenType
from .errors import ParseError


class Scanner:
    tokens = []
    start = -1
    current = -1
    line = 1
    
    def __init__(self, source: str):
        self.source = source

    def scan_tokens(self) -> list:
        while True:
            self.equlize_indexes()
            if self.is_at_end():
                break
            self.scan_token()

        self.add_token(TokenType.EOF)
        return Scanner.tokens

    def equlize_indexes(self):
        if Scanner.current > Scanner.start:
            Scanner.start = Scanner.current
        else:
            Scanner.current = Scanner.start

    def scan_token(self):
        c = self.advance()
        match c:
            case '-':
                if self.peek_start() == ' ':
                    self.add_token(TokenType.LIST_ENTRY)
                    Scanner.start += 1

                elif self.peek_start() == '-' and self.peek_next_current == '-':
                    self.add_token(TokenType.LIST_INNER)
                    Scanner.start += 2

                elif self.is_digit(self.peek()):
                    self.number()

            case ' ':
                Scanner.start += 1

            case '|':
                self.add_token(TokenType.BAR)

            case '!':
                if self.peek_start() != ' ':
                    self.obj()

            case '<':
                self.tag()

            case '\r':
                pass

            case '\t':
                pass

            case '\n':
                self.add_token(TokenType.NEW_LINE)

            case '~':
                if self.peek_start() == '~':
                    while self.peek_start() != '\n' and not self.is_at_end():
                        Scanner.start += 1

            case _:
                if self.is_digit(c):
                    self.number()
                    return

                self.other()

    def advance(self) -> str:
        Scanner.start += 1
        Scanner.current += 1
        return self.source[Scanner.start]

    def add_token(self, t_type: TokenType, lexeme: str=None, literal: object=None):
        Scanner.tokens.append(Token(t_type, lexeme, literal, Scanner.line, Scanner.start))

    def is_at_end(self, index: int=None):
        if index:
            return index + 1 >= len(self.source)
        return Scanner.current + 1 >= len(self.source)

    def is_digit(self, c: str) -> bool:
        return c >= '0' and c <= '9'

    def is_alpha(self, c: str) -> bool:
        return (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z') or c == '_'

    def is_alphanumeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def peek_start(self) -> str:
        if Scanner.start + 1 >= len(self.source):
            return ''
        return self.source[(Scanner.start + 1)]

    def peek_start_next(self) -> str:
        if Scanner.start + 2 >= len(self.source):
            return ''
        return self.source[(Scanner.start + 2)]

    def peek_current(self) -> str:
        if self.is_at_end():
            return ''
        return self.source[(Scanner.current + 1)]

    def peek_next_current(self) -> str:
        if Scanner.current + 1 >= len(self.source):
            return ''
        return self.source[(Scanner.current + 2)]

    def number(self):
        while self.is_digit(self.peek_current()):
            Scanner.current += 1

        if self.peek_current() in ('/', '.', '%', 'x', 'b'):
            Scanner.current += 1
            while self.is_digit(self.peek_current()):
                Scanner.current += 1

        number = self.source[Scanner.start:Scanner.current + 1]
        self.add_token(TokenType.NUMBER, number)

    def other(self):
        while self.is_alphanumeric(self.peek_current()) and not self.is_at_end():
            Scanner.current += 1

        text = self.source[Scanner.start:Scanner.current + 1].strip()
        if self.peek_current() == ':':
            Scanner.current += 1
            self.add_token(TokenType.DICT_KEY, text)
            return

        elif text == "true":
            self.add_token(TokenType.BOOL, None, True)
            return

        elif text == "false":
            self.add_token(TokenType.BOOL, None, False)
            return

        self.text()

    def text(self):
        if self.source[Scanner.start] == '"':
            if self.source[Scanner.start: Scanner.start + 3] == '"""':
                Scanner.start += 3
                lines = []
                while True:
                    if self.is_at_end():
                        raise ParseError(Scanner.line, "Have to close the multiline text quotes.")

                    if self.peek_current() == '\n':
                        Scanner.line += 1
                        lines.append(self.source[Scanner.start: Scanner.current + 1].strip())
                        Scanner.current += 1
                        self.equlize_indexes()

                    if self.peek_current() == '"':
                        if self.source[Scanner.current + 1: Scanner.current + 4] == '"""':
                            lines.append(self.source[Scanner.start: Scanner.current + 1])
                            self.equlize_indexes()
                            Scanner.start += 3
                            self.add_token(TokenType.MULTILINE, None, lines[1:-1])
                            return

                    Scanner.current += 1

            while True:
                if self.is_at_end():
                    raise ParseError(Scanner.line, "Have to close the text quotes.")

                if self.peek_current() == '\n':
                    raise ParseError(Scanner.line, "Have to close the text quotes")

                if self.peek_current() == '"':
                    text = self.source[Scanner.start: Scanner.current + 1]
                    Scanner.current += 1
                    self.add_token(TokenType.TEXT, None, text)
                    return

                Scanner.current += 1

        while self.peek_current() != '\n' and not self.is_at_end():
            Scanner.current += 1

        text = self.source[Scanner.start:Scanner.current + 1]
        self.add_token(TokenType.TEXT, None, text)

    def obj(self):
        if self.is_digit(self.source[Scanner.start + 1]):
            raise ParseError(Scanner.line, "Object name can't start with a digit")
            return

        while self.is_alphanumeric(self.peek_current()):
            Scanner.current += 1

        token = self.source[Scanner.start + 1:Scanner.current + 1]
        self.add_token(TokenType.OBJECT, token)

    def tag(self):
        if self.peek_current() == '/':
            Scanner.current += 1
            if not self.is_alpha(self.peek_next_current()):
                raise ParseError(Scanner.line, "Tag has to start with a alpha character or slash.")

            while self.is_alphanumeric(self.peek_current()):
                Scanner.current += 1

            if self.peek_current() == "|" and self.peek_next_current() == ">":
                Scanner.current += 2
                tag = self.source[Scanner.start + 2: Scanner.current - 1]
                self.add_token(TokenType.TAG, None, tag)
                return
            else:
                raise ParseError(Scanner.line, "Partial Tag. Invalid syntax.")

        while self.is_alphanumeric(self.peek_current()) and not self.is_at_end():
            Scanner.current += 1

        if self.peek_current() == '>':
            tag = self.source[Scanner.start + 1: Scanner.current + 1]
            Scanner.current += 1

            while not self.is_at_end():
                if self.is_at_end():
                    raise ParseError(Scanner.line, "Closing tag not found.")

                if self.peek_current() == '<':
                    if self.source[Scanner.current + 1:(Scanner.current + len(tag) + 4)] == f"</{tag}>":
                        Scanner.current += (len(tag) + 3)
                        content = self.source[(Scanner.start + len(tag) + 2):(Scanner.current - (len(tag) + 2))]
                        self.add_token(TokenType.TAG, content, tag)
                        return

                Scanner.current += 1
