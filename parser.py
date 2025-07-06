from typing import List, Tuple

from buffered_scanner import BufferedScanner
from diagnostics import Diagnostics
from syntax import (
    Add,
    Assignment,
    BlockStmt,
    Declaration,
    Div,
    EqualEqualExpr,
    Expression,
    ExprStmt,
    FalseExpr,
    GreaterEqualExpr,
    GreaterThanExpr,
    Grouping,
    IfStmt,
    LessEqualExpr,
    LessThanExpr,
    LogicalAnd,
    LogicalNot,
    LogicalOr,
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
    AND,
    BANG,
    BANG_EQUAL,
    ELSE,
    EOF,
    EQUAL,
    EQUAL_EQUAL,
    FALSE,
    GREATER,
    GREATER_EQUAL,
    IDENT,
    IF,
    LBRACE,
    LESS,
    LESS_EQUAL,
    LPAREN,
    MINUS,
    NIL,
    NUMBER,
    OR,
    PLUS,
    PRINT,
    RBRACE,
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


def _parse_logical_and(tokens: BufferedScanner) -> Expression:
    expr = _parse_equality(tokens)
    while tokens.has_next():
        diag = tokens.diagnostics()
        if tokens.eat(AND()):
            expr = LogicalAnd(expr, _parse_equality(tokens), diag=diag)
        else:
            break

    return expr


def _parse_logical_or(tokens: BufferedScanner) -> Expression:
    expr = _parse_logical_and(tokens)
    while tokens.has_next():
        diag = tokens.diagnostics()
        if tokens.eat(OR()):
            expr = LogicalOr(expr, _parse_logical_and(tokens), diag=diag)
        else:
            break

    return expr


# Syntax:
#
# Program       -> Declaration* EOF
# Declaration   -> VarDecl
#                  | Statement
# VarDecl       -> VAR IDENT (EQUAL Expression)? SEMICOLON
# Statement     -> PrintStmt
#                  | ExprStmt
# PrintStmt     -> PRINT LPAREN Expression RPAREN SEMICOLON
# ExprStmt      -> Expression SEMICOLON
#
# TODO:
# - Add support for assignments like a.b.c = 3.
# - Add blocks ({ statement; statement; })
# - Add if statements
# - Add function definitions
# - Add function calls
# - Add classes
# - ...?
#
#
# Expression    -> Assignment
# Assignment    -> IDENT EQUAL Expression
#                  | Equality
# Equality      -> Comparison ( ("==" | "!=") Comparison)*
# Comparison    -> Term ( ( "<" | "<=" | ">" | ">=" ) Term)*
# Term          -> Factor ( ( "+" | "-") Factor )*
# Factor        -> Unary ( ( "*" | "/" ) Unary )*
# Unary         -> ( "-" | "!" ) Primary
#                  | "+" Expression -> error production
#                  | Primary
# Primary       -> NUMBER | STRING | TRUE | FALSE | NIL | IDENT
#                  | "(" Expression ")"


def _parse_assign_or_equality(tokens: BufferedScanner) -> Expression:
    # Parse first IDENT as an expression.
    diag = tokens.diagnostics()

    # This is the place where we can't do one-token-lookahead parsing. This will be even
    # more true once lvalues become more complex things than just a single identifier.
    # We try to parse the tokens as an equality. If that's equal to a simple identifier
    # node followed by an equal sign, we convert the parsed equality node (which is
    # a variable node) to an assignment node.
    ident_or_equality = _parse_logical_or(tokens)
    diag = tokens.diagnostics()
    if tokens.eat(EQUAL()):
        if not isinstance(ident_or_equality, Variable):
            raise ParserError("Invalid lvalue", diag)
        return Assignment(
            ident_or_equality.name, _parse_assign_or_equality(tokens), diag=diag
        )
    else:
        return ident_or_equality


def parse_expression(tokens: BufferedScanner) -> Expression:
    return _parse_assign_or_equality(tokens)


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
    if not tokens.eat(SEMICOLON()):
        raise ParserError(
            "Missing semicolon after print statement", tokens.diagnostics()
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
        decl = VarDecl(name, parse_expression(tokens), diag=diag)
    else:
        decl = VarDecl(name, None, diag=diag)
    if not tokens.eat(SEMICOLON()):
        raise ParserError(
            "Missing semicolon after variable declaration", tokens.diagnostics()
        )

    return decl


def _parse_if_statement(tokens: BufferedScanner) -> IfStmt:
    diag = tokens.diagnostics()
    tokens.eat(IF())
    lparen_diag = tokens.diagnostics()
    if not tokens.eat(LPAREN()):
        raise ParserError("Expected '(' after 'if'", tokens.diagnostics())
    condition = parse_expression(tokens)
    if not tokens.eat(RPAREN()):
        raise ParserError(
            "Expected ')' after if condition",
            tokens.diagnostics(),
            [("Opening parenthesis here", lparen_diag)],
        )

    then_branch = parse_statement(tokens)
    else_branch = None
    if tokens.eat(ELSE()):
        else_branch = parse_statement(tokens)

    return IfStmt(condition, then_branch, else_branch, diag=diag)


def parse_statement(tokens) -> Statement:
    diag = tokens.diagnostics()
    match tokens.peek():
        case PRINT():
            stmt = _parse_print_stmt(tokens)
        case LBRACE():
            stmt = _parse_block_stmt(tokens)
        case IF():
            stmt = _parse_if_statement(tokens)
        case _:
            # ExprStmt parsed here, contains a semicolon.
            # The Expression doesnt.
            stmt = ExprStmt(parse_expression(tokens), diag=diag)
            if not tokens.eat(SEMICOLON()):
                raise ParserError(
                    "Missing semicolon after expression statement", tokens.diagnostics()
                )

    return stmt


def _parse_declaration(tokens: BufferedScanner) -> Declaration:
    match tokens.peek():
        case VAR():
            stmt = _parse_var_decl(tokens)
        case _:
            stmt = parse_statement(tokens)
    return stmt


def parse_program(tokens: BufferedScanner) -> Program:
    # Currently only a single expression is supported.
    if tokens.eat(EOF()):
        # No expression (empty program)
        return Program([])

    declarations = []
    while tokens.has_next() and tokens.peek() != EOF():
        declarations.append(_parse_declaration(tokens))

    if not tokens.has_next():
        raise ParserError("Unexpected end of input, expected EOF", tokens.diagnostics())
    if not tokens.eat(EOF()):
        raise ParserError(
            "Unexpected token; expected end-of-file", tokens.diagnostics()
        )
    return Program(declarations)


def _parse_block_stmt(tokens: BufferedScanner) -> BlockStmt:
    diag = tokens.diagnostics()
    lbrace_diag = tokens.diagnostics()
    tokens.eat(LBRACE())

    declarations = []
    while tokens.has_next() and tokens.peek() != RBRACE():
        if tokens.peek() == EOF():
            raise ParserError(
                "Expected '}' after block",
                tokens.diagnostics(),
                [("Opening brace here", lbrace_diag)],
            )
        declarations.append(_parse_declaration(tokens))

    if not tokens.has_next():
        raise ParserError(
            "Expected '}' after block",
            tokens.diagnostics(),
            [("Opening brace here", lbrace_diag)],
        )

    if not tokens.eat(RBRACE()):
        raise ParserError(
            "Expected '}' after block",
            tokens.diagnostics(),
            [("Opening brace here", lbrace_diag)],
        )

    return BlockStmt(declarations, diag=diag)
