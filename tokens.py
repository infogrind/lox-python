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
class LBRACE(Token):
    pass


@dataclass
class RBRACE(Token):
    pass


@dataclass
class COMMA(Token):
    pass


@dataclass
class DOT(Token):
    pass


@dataclass
class MINUS(Token):
    pass


@dataclass
class PLUS(Token):
    pass


@dataclass
class SEMICOLON(Token):
    pass


@dataclass
class SLASH(Token):
    pass


# One or two character tokens


@dataclass
class BANG(Token):
    pass


@dataclass
class BANG_EQUAL(Token):
    pass


@dataclass
class EQUAL(Token):
    pass


@dataclass
class GREATER(Token):
    pass


@dataclass
class GREATER_EQUAL(Token):
    pass


@dataclass
class LESS(Token):
    pass


@dataclass
class LESS_EQUAL(Token):
    pass


# Literals


@dataclass
class IDENT(Token):
    name: str


@dataclass
class STRING(Token):
    value: str


@dataclass
class NUMBER(Token):
    pass


# Keywords


@dataclass
class AND(Token):
    pass


@dataclass
class CLASS(Token):
    pass


@dataclass
class ELSE(Token):
    pass


@dataclass
class FALSE(Token):
    pass


@dataclass
class FUN(Token):
    pass


@dataclass
class FOR(Token):
    pass


@dataclass
class IF(Token):
    pass


@dataclass
class NIL(Token):
    pass


@dataclass
class OR(Token):
    pass


@dataclass
class PRINT(Token):
    pass


@dataclass
class RETURN(Token):
    pass


@dataclass
class SUPER(Token):
    pass


@dataclass
class TRUE(Token):
    pass


@dataclass
class VAR(Token):
    pass


@dataclass
class WHILE(Token):
    pass
