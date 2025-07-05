from dataclasses import dataclass, field
from typing import List

from diagnostics import Diagnostics

# Syntax:
#
# Program       -> Declaration* EOF
# Declaration   -> VarDecl
#                  | Statement
# VarDecl       -> VAR IDENT (EQUAL Expression)? SEMICOLON
# Statement     -> PrintStmt
#                  | ExprStmt
#                  | BlockStmt
# PrintStmt     -> PRINT LPAREN Expression RPAREN SEMICOLON
# ExprStmt      -> Expression SEMICOLON
# BlockStmt     -> LBRACE Declaration* RBRACE
#
# TODO:
# - Add support for assignments like a.b.c = 3.
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


@dataclass
class Declaration:
    diag: Diagnostics = field(kw_only=True)


@dataclass
class Program:
    decls: List[Declaration]


class Statement(Declaration):
    pass


@dataclass
class Expression:
    diag: Diagnostics = field(kw_only=True)


class LiteralExpression(Expression):
    pass


@dataclass
class Number(LiteralExpression):
    value: float


@dataclass
class String(LiteralExpression):
    value: str


@dataclass
class TrueExpr(LiteralExpression):
    pass


@dataclass
class FalseExpr(LiteralExpression):
    pass


@dataclass
class Nil(LiteralExpression):
    pass


@dataclass
class Variable(LiteralExpression):
    name: str


@dataclass
class Grouping(Expression):
    expr: Expression


@dataclass
class Negative(Expression):
    expr: Expression


@dataclass
class LogicalNot(Expression):
    expr: Expression


@dataclass
class EqualEqualExpr(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class NotEqualExpr(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class LessThanExpr(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class LessEqualExpr(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class GreaterThanExpr(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class GreaterEqualExpr(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class Add(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class Subtract(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class Mult(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class Div(Expression):
    lhs: Expression
    rhs: Expression


@dataclass
class PrintStmt(Statement):
    expr: Expression


@dataclass
class ExprStmt(Statement):
    expr: Expression


@dataclass
class VarDecl(Declaration):
    name: str
    expr: Expression | None


@dataclass
class Assignment(Expression):
    target: str
    expr: "Assignment"


@dataclass
class BlockStmt(Statement):
    declarations: List[Declaration]
