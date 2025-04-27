from buffered_scanner import BufferedScanner
from diagnostics import Diagnostics
from syntax import (
    Add,
    Div,
    EqualEqualExpr,
    Expression,
    FalseExpr,
    GreaterEqualExpr,
    GreaterThanExpr,
    LessEqualExpr,
    LessThanExpr,
    LogicalNot,
    Mult,
    Negative,
    Nil,
    NotEqualExpr,
    Number,
    Program,
    String,
    Subtract,
    TrueExpr,
)
from tokens import (
    BANG,
    BANG_EQUAL,
    EOF,
    EQUAL_EQUAL,
    FALSE,
    GREATER,
    GREATER_EQUAL,
    LESS,
    LESS_EQUAL,
    LPAREN,
    MINUS,
    NIL,
    NUMBER,
    PLUS,
    RPAREN,
    SLASH,
    STAR,
    STRING,
    TRUE,
)


class ParserError(Exception):
    def __init__(self, message, diagnostics):
        super().__init__(message)
        self.message: str = message
        self.diagnostics: Diagnostics = diagnostics


def _parse_primary(tokens: BufferedScanner) -> Expression:
    diag = tokens.diagnostics()
    if not tokens.has_next():
        raise ParserError("Unexpected end of expression", diag)
    t = tokens.next()
    match t:
        case NUMBER(value):
            return Number(value, diag=diag)
        case STRING(value):
            return String(value, diag=diag)
        case TRUE():
            return TrueExpr(diag=diag)
        case FALSE():
            return FalseExpr(diag=diag)
        case NIL():
            return Nil(diag=diag)
        case LPAREN():
            expr = _parse_expression(tokens)
            if not tokens.eat(RPAREN()):
                raise ParserError("Missing closing parenthesis", tokens.diagnostics())
            return expr
        case PLUS() | SLASH() | STAR():
            raise ParserError("Illegal start of expression", diag)
        case _:
            raise ParserError(f"Unexpected token {t} while parsing primary", diag)


def _parse_unary(tokens: BufferedScanner) -> Expression:
    diag = tokens.diagnostics()
    if tokens.eat(BANG()):
        expr = LogicalNot(_parse_unary(tokens), diag=diag)
    elif tokens.eat(MINUS()):
        expr = Negative(_parse_unary(tokens), diag=diag)
    else:
        expr = _parse_primary(tokens)

    return expr


def _parse_factor(tokens: BufferedScanner) -> Expression:
    expr = _parse_unary(tokens)
    while tokens.has_next():
        diag = tokens.diagnostics()
        if tokens.eat(STAR()):
            expr = Mult(expr, _parse_unary(tokens), diag=diag)
        elif tokens.eat(SLASH()):
            expr = Div(expr, _parse_unary(tokens), diag=diag)
        else:
            break

    return expr


def _parse_term(tokens: BufferedScanner) -> Expression:
    expr = _parse_factor(tokens)
    while tokens.has_next():
        diag = tokens.diagnostics()
        if tokens.eat(PLUS()):
            expr = Add(expr, _parse_factor(tokens), diag=diag)
        elif tokens.eat(MINUS()):
            expr = Subtract(expr, _parse_factor(tokens), diag=diag)
        else:
            break

    return expr


def _parse_comparison(tokens: BufferedScanner) -> Expression:
    expr = _parse_term(tokens)
    while tokens.has_next():
        diag = tokens.diagnostics()
        if tokens.eat(LESS()):
            expr = LessThanExpr(expr, _parse_term(tokens), diag=diag)
        elif tokens.eat(LESS_EQUAL()):
            expr = LessEqualExpr(expr, _parse_term(tokens), diag=diag)
        elif tokens.eat(GREATER()):
            expr = GreaterThanExpr(expr, _parse_term(tokens), diag=diag)
        elif tokens.eat(GREATER_EQUAL()):
            expr = GreaterEqualExpr(expr, _parse_term(tokens), diag=diag)
        else:
            break

    return expr


def _parse_equality(tokens: BufferedScanner) -> Expression:
    expr = _parse_comparison(tokens)
    while tokens.has_next():
        diag = tokens.diagnostics()
        if tokens.eat(EQUAL_EQUAL()):
            expr = EqualEqualExpr(expr, _parse_comparison(tokens), diag=diag)
        elif tokens.eat(BANG_EQUAL()):
            expr = NotEqualExpr(expr, _parse_comparison(tokens), diag=diag)
        else:
            break

    return expr


# Syntax:
#
# Program       -> (Expression)?
# Expression    -> Equality
# Equality      -> Comparison ( ("==" | "!=") Comparison)*
# Comparison    -> Term ( ( "<" | "<=" | ">" | ">=" ) Term)*
# Term          -> Factor ( ( "+" | "-") Factor )*
# Factor        -> Unary ( ( "*" | "/" ) Unary )*
# Unary         -> ( "-" | "!" ) Primary
#                  | "+" Expression -> error production
#                  | Primary
# Primary       -> NUMBER | STRING | TRUE | FALSE | NIL
#                  | "(" Expression ")"


def _parse_expression(tokens: BufferedScanner) -> Expression:
    return _parse_equality(tokens)


def parse_program(tokens: BufferedScanner) -> Program:
    # Currently only a single expression is supported.
    if tokens.eat(EOF()):
        # No expression (empty program)
        return Program(None)

    expr = _parse_expression(tokens)
    if not tokens.eat(EOF()):
        raise ParserError(
            "Unexpected token; expected end-of-file", tokens.diagnostics()
        )
    return Program(expr)
