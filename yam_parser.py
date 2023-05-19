from scanner import Scanner
from icecream import ic


def parse(file_path, *class_references, **tag_references):
    with open(file_path, "r") as f:
        source = f.read()

    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    ic(tokens)
