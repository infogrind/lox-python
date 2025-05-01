import sys
from typing import Generator, Iterator

from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from charreader import CharReader
from expression_evaluator import TypeError, evaluate_expression
from parser import ParserError, parse_statement
from syntax import Expression, PrintStmt, Statement
from token_generator import ScannerError, token_generator


def lazy_readlines(filename: str) -> Generator[str, None, None]:
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            yield str(line)


def _evaluate_lines(lines: Iterator[str]) -> None:
    try:
        s: Statement = parse_statement(
            BufferedScanner(BufferedIterator(token_generator(CharReader(lines))))
        )
        match s:
            case Expression():
                print(evaluate_expression(s))
            case PrintStmt():
                # TODO: Consider different behavior for expressions and print statements
                print(evaluate_expression(s.expr))
    except ScannerError as e:
        print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
    except ParserError as e:
        print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
        for m, d in e.additional:
            print(f"{m}:\n{d.diagnostic_string()}")
    except TypeError as e:
        print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
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
