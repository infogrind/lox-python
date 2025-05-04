from typing import List, Tuple

from buffered_scanner import BufferedScanner
from diagnostics import Diagnostics
from syntax import (
    Add,
    Assignment,
    Div,
    EqualEqualExpr,
    Expression,
    FalseExpr,
    GreaterEqualExpr,
    GreaterThanExpr,
    Grouping,
    LessEqualExpr,
    LessThanExpr,
    LogicalNot,
    Mult,
    Negative,
    Nil,
    NotEqualExpr,
    Number,
    PrintStmt,
    Program,
    Statement,
    String,
    Subtract,
    TrueExpr,
    VarDecl,
    Variable,
)
from tokens import (
    BANG,
    BANG_EQUAL,
    EOF,
    EQUAL,
    EQUAL_EQUAL,
    FALSE,
    GREATER,
    GREATER_EQUAL,
    IDENT,
    LESS,
    LESS_EQUAL,
    LPAREN,
    MINUS,
    NIL,
    NUMBER,
    PLUS,
    PRINT,
    RPAREN,
    SEMICOLON,
    SLASH,
    STAR,
    STRING,
    TRUE,
    VAR,
)


class ParserError(Exception):
    def __init__(
        self,
        message: str,
        diagnostics: Diagnostics,
        additional: List[Tuple[str, Diagnostics]] = [],
    ):
        super().__init__(message)
        self.message: str = message
        self.diagnostics: Diagnostics = diagnostics
        self.additional: List[Tuple[str, Diagnostics]] = additional


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
        case IDENT(name):
            return Variable(name, diag=diag)
        case LPAREN():
            start_paren_diag = diag
            expr = Grouping(parse_expression(tokens), diag=diag)
            if not tokens.eat(RPAREN()):
                raise ParserError(
                    "Missing closing parenthesis",
                    tokens.diagnostics(),
                    [("Opening parenthesis here", start_paren_diag)],
                )
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
# Program       -> (Statement SEMICOLON)*
# Statement     -> PrintStmt
#                  | VarDecl
#                  | Assignment
#                  | Expression
# PrintStmt     -> PRINT LPAREN Expression RPAREN
# VarDecl       -> VAR IDENT (EQUAL Expression)?
#
# TODO: Add support for assignments like a.b.c = 3
#
# Assignment    -> IDENT EQUAL Expression
# Lvalue        -> IDENT (DOT IDENT)*
# Expression    -> Equality
# Equality      -> Comparison ( ("==" | "!=") Comparison)*
# Comparison    -> Term ( ( "<" | "<=" | ">" | ">=" ) Term)*
# Term          -> Factor ( ( "+" | "-") Factor )*
# Factor        -> Unary ( ( "*" | "/" ) Unary )*
# Unary         -> ( "-" | "!" ) Primary
#                  | "+" Expression -> error production
#                  | Primary
# Primary       -> NUMBER | STRING | TRUE | FALSE | NIL | IDENT
#                  | "(" Expression ")"


def parse_expression(tokens: BufferedScanner) -> Expression:
    return _parse_equality(tokens)


def _parse_print_stmt(tokens: BufferedScanner) -> PrintStmt:
    diag = tokens.diagnostics()
    tokens.eat(PRINT())
    lparen_diag = tokens.diagnostics()
    if not tokens.eat(LPAREN()):
        raise ParserError("Unexpected token, expected '('", tokens.diagnostics())
    stmt = PrintStmt(parse_expression(tokens), diag=diag)
    if not tokens.eat(RPAREN()):
        raise ParserError(
            "Missing closing parenthesis in print statement",
            tokens.diagnostics(),
            [("Opening parenthesis here", lparen_diag)],
        )

    return stmt


def _parse_var_decl(tokens: BufferedScanner) -> VarDecl:
    diag = tokens.diagnostics()
    tokens.eat(VAR())
    match tokens.peek():
        case IDENT(s):
            tokens.next()
            name = s
        case _:
            raise ParserError("Unexpected token", tokens.diagnostics())

    if tokens.eat(EQUAL()):
        return VarDecl(name, parse_expression(tokens), diag=diag)
    else:
        return VarDecl(name, None, diag=diag)


def _parse_assign_or_expr(tokens: BufferedScanner) -> Statement:
    # Parse first IDENT as an expression.
    diag = tokens.diagnostics()
    ident_expr = parse_expression(tokens)
    if tokens.eat(EQUAL()):
        assert isinstance(ident_expr, Variable)
        return Assignment(ident_expr.name, parse_expression(tokens), diag=diag)
    else:
        return ident_expr


def parse_statement(tokens) -> Statement:
    match tokens.peek():
        case PRINT():
            stmt = _parse_print_stmt(tokens)
        case VAR():
            stmt = _parse_var_decl(tokens)
        case IDENT(_):
            stmt = _parse_assign_or_expr(tokens)
        case _:
            stmt = parse_expression(tokens)

    if not tokens.eat(SEMICOLON()):
        raise ParserError("Missing semicolon after statement", tokens.diagnostics())
    return stmt


def parse_program(tokens: BufferedScanner) -> Program:
    # Currently only a single expression is supported.
    if tokens.eat(EOF()):
        # No expression (empty program)
        return Program([])

    statements = []
    while tokens.has_next() and tokens.peek() != EOF():
        statements.append(parse_statement(tokens))

    if not tokens.has_next():
        raise ParserError("Unexpected end of input, expected EOF", tokens.diagnostics())
    if not tokens.eat(EOF()):
        raise ParserError(
            "Unexpected token; expected end-of-file", tokens.diagnostics()
        )
    return Program(statements)
