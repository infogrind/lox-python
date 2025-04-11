from tokens import LPAREN, RPAREN, IDENT, EQUAL, STRING
from scanner import scan


def read_tokens() -> None:
    for token in scan():
        match token:
            case LPAREN():
                print("LPAREN")
            case RPAREN():
                print("RPAREN")
            case IDENT(name):
                print(f"IDENT({name})")
            case EQUAL():
                print("EQUAL")
            case STRING(value):
                print(f"STRING({value})")
