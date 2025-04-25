from typing import Generator
from token_generator import token_generator, ScannerError
from tokens import Token
from charreader import CharReader
from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from parser import parse_node, ParserError
from ast_printer import print_node
import sys


def lazy_readlines(filename: str) -> Generator[str, None, None]:
    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            yield str(line)


def scan_file(filename: str) -> None:
    print(
        print_node(
            parse_node(
                BufferedScanner(
                    BufferedIterator(
                        token_generator(CharReader(lazy_readlines(filename)))
                    )
                )
            )
        )
    )


def scan_input() -> None:
    print("Enter some code (ctrl-d to exit):")
    while True:
        try:
            line = input("> ")
            print(
                print_node(
                    parse_node(
                        BufferedScanner(
                            BufferedIterator(
                                token_generator((CharReader(iter([line]))))
                            )
                        )
                    )
                )
            )
        except EOFError:
            break
        except ParserError as e:
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
