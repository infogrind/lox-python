from typing import Generator
from token_generator import token_generator, ScannerError
from charreader import CharReader
from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from parser import parse_program, ParserError
from syntax import Program
from expression_evaluator import evaluate_expression, TypeError
from typing import Iterator
import sys


def lazy_readlines(filename: str) -> Generator[str, None, None]:
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            yield str(line)


def _evaluate_lines(lines: Iterator[str]) -> None:
    try:
        p: Program = parse_program(
            BufferedScanner(BufferedIterator(token_generator(CharReader(lines))))
        )
        if not p.expr:
            print("empty program")
            return
        print(evaluate_expression(p.expr))
    except ScannerError as e:
        print(f"{e}")
    except ParserError as e:
        print(f"{e}")
    except TypeError as e:
        print(f"{e}")
    except ZeroDivisionError:
        print("Division by zero")


def scan_file(filename: str) -> None:
    _evaluate_lines(lazy_readlines(filename))


def scan_input() -> None:
    print("Enter some code (ctrl-d to exit):")
    while True:
        try:
            line = input("> ")
            _evaluate_lines(iter([line]))
        except EOFError:
            break


def main() -> None:
    if len(sys.argv) > 2:
        print("Syntax error.")

    if len(sys.argv) == 2:
        scan_file(sys.argv[1])
    else:
        scan_input()


if __name__ == "__main__":
    main()
