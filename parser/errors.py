class ParseError(Exception):
    def __init__(self, line: int, message: str):
        super().__init__(f"[line {line}]: {message}")
