from scanner import Scanner
from parser import Parser
from icecream import ic


def parse(file_path: str, *class_references, **tag_references):
    try:
        with open(file_path, "r") as f:
            source = f.read()

        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        ic(tokens)

        parser = Parser(tokens)
        data = parser.parse()

        return data

    except Exception as e:
        raise e
