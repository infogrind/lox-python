from buffered_scanner import BufferedScanner
from tokens import (
    Token,
    LPAREN,
    RPAREN,
    LBRACE,
    RBRACE,
    COMMA,
    DOT,
    MINUS,
    PLUS,
    SEMICOLON,
    SLASH,
    STAR,
    BANG,
    BANG_EQUAL,
    EQUAL,
    EQUAL_EQUAL,
    GREATER,
    GREATER_EQUAL,
    LESS,
    LESS_EQUAL,
    IDENT,
    STRING,
    NUMBER,
    AND,
    CLASS,
    ELSE,
    FALSE,
    FUN,
    FOR,
    IF,
    NIL,
    OR,
    PRINT,
    RETURN,
    SUPER,
    THIS,
    TRUE,
    VAR,
    WHILE,
)
from syntax import (
    Node,
    Expression,
    Number,
    String,
    Negative,
    LogicalNot,
    Grouping,
    LessEqualExpr,
    LessThanExpr,
    GreaterEqualExpr,
    GreaterThanExpr,
    EqualEqualExpr,
    NotEqualExpr,
    Add,
    Subtract,
    Mult,
    Div,
    TrueExpr,
    FalseExpr,
    Nil,
)


class ParserError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _parse_primary(tokens: BufferedScanner) -> Expression:
    diag = tokens.diagnostics()
    if not tokens.has_next():
        raise ParserError("Unexpected end of expression:\n" + diag)
    t = tokens.next()
    match t:
        case NUMBER(value):
            return Number(value)
        case STRING(value):
            return String(value)
        case TRUE():
            return TrueExpr()
        case FALSE():
            return FalseExpr()
        case NIL():
            return Nil()
        case LPAREN():
            expr = _parse_expression(tokens)
            if not tokens.eat(RPAREN()):
                raise ParserError(
                    "Missing closing parenthesis:\n"
                    + tokens.diagnostics()
                    + "\nStarting parenthesis:\n"
                    + diag
                )
            return expr
        case PLUS() | SLASH() | STAR():
            raise ParserError("Illegal start of expression:\n" + diag)
        case _:
            raise ParserError(f"Unexpected token {t} while parsing primary:\n" + diag)


def _parse_unary(tokens: BufferedScanner) -> Expression:
    if tokens.eat(BANG()):
        expr = LogicalNot(_parse_unary(tokens))
    elif tokens.eat(MINUS()):
        expr = Negative(_parse_unary(tokens))
    else:
        expr = _parse_primary(tokens)

    return expr


def _parse_factor(tokens: BufferedScanner) -> Expression:
    expr = _parse_unary(tokens)
    while tokens.has_next():
        if tokens.eat(STAR()):
            expr = Mult(expr, _parse_unary(tokens))
        elif tokens.eat(SLASH()):
            expr = Div(expr, _parse_unary(tokens))
        else:
            break

    return expr


def _parse_term(tokens: BufferedScanner) -> Expression:
    expr = _parse_factor(tokens)
    while tokens.has_next():
        if tokens.eat(PLUS()):
            expr = Add(expr, _parse_factor(tokens))
        elif tokens.eat(MINUS()):
            expr = Subtract(expr, _parse_factor(tokens))
        else:
            break

    return expr


def _parse_comparison(tokens: BufferedScanner) -> Expression:
    # TODO: Parse intermediary levels
    expr = _parse_term(tokens)
    while tokens.has_next():
        if tokens.eat(LESS()):
            expr = LessThanExpr(expr, _parse_term(tokens))
        elif tokens.eat(LESS_EQUAL()):
            expr = LessEqualExpr(expr, _parse_term(tokens))
        elif tokens.eat(GREATER()):
            expr = GreaterThanExpr(expr, _parse_term(tokens))
        elif tokens.eat(GREATER_EQUAL()):
            expr = GreaterEqualExpr(expr, _parse_term(tokens))
        else:
            break

    return expr


def _parse_equality(tokens: BufferedScanner) -> Expression:
    expr = _parse_comparison(tokens)
    while tokens.has_next():
        if tokens.eat(EQUAL_EQUAL()):
            expr = EqualEqualExpr(expr, _parse_comparison(tokens))
        elif tokens.eat(BANG_EQUAL()):
            expr = NotEqualExpr(expr, _parse_comparison(tokens))
        else:
            break

    return expr


# Syntax:
#
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


def parse_node(tokens: BufferedScanner) -> Node:
    # Currently only a single expression is supported.
    expr = _parse_expression(tokens)
    if tokens.has_next():
        raise RuntimeError(f"Unexpected token after expression: {tokens.peek()}")
    return expr
