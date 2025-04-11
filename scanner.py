from tokens import Token, LPAREN, RPAREN, IDENT, EQUAL, STRING
from typing import Iterator


def scan() -> Iterator[Token]:
    yield LPAREN()
    yield IDENT("Foo")
    yield EQUAL()
    yield STRING("Bar")
    yield RPAREN()
