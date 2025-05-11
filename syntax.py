from dataclasses import dataclass, field
from typing import List

from diagnostics import Diagnostics


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
