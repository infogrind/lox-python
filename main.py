from typing import Generator
from scanner import Scanner, ScannerError
from charreader import CharReader
import sys


def lazy_readlines(filename: str) -> Generator[str, None, None]:
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            yield str(line)


def print_tokens(scanner: Scanner) -> None:
    while scanner.has_next():
        print(f"Token: {scanner.next()}")


def scan_file(filename: str) -> None:
    print_tokens(Scanner(CharReader(lazy_readlines(filename))))


def scan_input() -> None:
    print("Enter some code (ctrl-d to exit):")
    while True:
        try:
            line = input("> ")
            print_tokens(Scanner(CharReader(iter([line]))))
        except EOFError:
            break
        except ScannerError as e:
            print(f"{e}")


def main() -> None:
    print(sys.argv)
    if len(sys.argv) > 2:
        print("Syntax error.")

    if len(sys.argv) == 2:
        scan_file(sys.argv[1])
    else:
        scan_input()


if __name__ == "__main__":
    main()
