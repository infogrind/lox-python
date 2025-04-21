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


def _parse_primary(tokens: BufferedScanner) -> Expression:
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
                raise RuntimeError("Missing closing parenthesis.")
            return expr
        case _:
            raise RuntimeError(f"Unexpected token {t} file parsing primary.")


def _parse_term(tokens: BufferedScanner) -> Expression:
    expr = _parse_primary(tokens)
    while tokens.has_next():
        if tokens.eat(PLUS()):
            expr = Add(expr, _parse_primary(tokens))
        elif tokens.eat(MINUS()):
            expr = Subtract(expr, _parse_primary(tokens))
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
