import sys
from typing import Generator

from expression_evaluator import TypeError, VariableError
from interpreter import Interpreter
from parser import ParserError
from token_generator import ScannerError


def lazy_readlines(filename: str) -> Generator[str, None, None]:
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            yield str(line)


def scan_file(filename: str) -> None:
    try:
        Interpreter().interpret(lazy_readlines(filename))
    except ScannerError as e:
        print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
    except ParserError as e:
        print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
        for m, d in e.additional:
            print(f"{m}:\n{d.diagnostic_string()}")
    except TypeError as e:
        print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
    except VariableError as e:
        print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
    except ZeroDivisionError:
        print("Division by zero")


def scan_input() -> None:
    i = Interpreter()
    print("Enter some code (ctrl-d to exit):")
    while True:
        try:
            line = input("> ")
            i.interpret(line)
        except ScannerError as e:
            print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
        except ParserError as e:
            print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
            for m, d in e.additional:
                print(f"{m}:\n{d.diagnostic_string()}")
        except TypeError as e:
            print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
        except VariableError as e:
            print(f"{e.message}:\n{e.diagnostics.diagnostic_string()}")
        except ZeroDivisionError:
            print("Division by zero")
        except EOFError:
            break


def main() -> None:
    if len(sys.argv) > 2:
        print("Syntax error.")
        sys.exit(1)

    if len(sys.argv) == 2:
        scan_file(sys.argv[1])
    else:
        scan_input()


if __name__ == "__main__":
    main()
