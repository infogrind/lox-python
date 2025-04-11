from dataclasses import dataclass


@dataclass
class Token:
    pass


@dataclass
class LPAREN(Token):
    pass


@dataclass
class RPAREN(Token):
    pass


@dataclass
class IDENT(Token):
    name: str


@dataclass
class STRING(Token):
    value: str


@dataclass
class EQUAL(Token):
    pass
