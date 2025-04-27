from diagnostics import Diagnostics
from syntax import (
    Add,
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
    Subtract,
    TrueExpr,
)


class TypeError(Exception):
    def __init__(self, message: str, diag: Diagnostics):
        super().__init__(message)
        self.message: str = message
        self.diagnostics: Diagnostics = diag


def _evaluate_number(expr: Expression) -> float:
    x = evaluate_expression(expr)
    if not isinstance(x, float):
        raise TypeError("Expected: number", expr.diag)
    return x


def _evaluate_bool(expr: Expression) -> bool:
    x = evaluate_expression(expr)
    if not isinstance(x, bool):
        raise TypeError("Expected: bool", expr.diag)
    return x


def evaluate_expression(expr: Expression) -> float | bool | None:
    match expr:
        # Primaries
        case Number(v):
            return v
        case TrueExpr():
            return True
        case FalseExpr():
            return False
        case Nil():
            return None
        case Grouping(expr):
            return evaluate_expression(expr)
        # Unary
        case Negative(expr):
            x = _evaluate_number(expr)
            return -x
        case LogicalNot(expr):
            x = _evaluate_bool(expr)
            return not x
        # Factors
        case Mult(lhs, rhs):
            x = _evaluate_number(lhs)
            y = _evaluate_number(rhs)
            return x * y
        case Div(lhs, rhs):
            x = _evaluate_number(lhs)
            y = _evaluate_number(rhs)
            return x / y
        # Terms
        case Add(lhs, rhs):
            x = _evaluate_number(lhs)
            y = _evaluate_number(rhs)
            return x + y
        case Subtract(lhs, rhs):
            x = _evaluate_number(lhs)
            y = _evaluate_number(rhs)
            return x - y
        # Comparisons
        case LessThanExpr(lhs, rhs):
            x = _evaluate_number(lhs)
            y = _evaluate_number(rhs)
            return x < y
        case LessEqualExpr(lhs, rhs):
            x = _evaluate_number(lhs)
            y = _evaluate_number(rhs)
            return x <= y
        case GreaterThanExpr(lhs, rhs):
            x = _evaluate_number(lhs)
            y = _evaluate_number(rhs)
            return x > y
        case GreaterEqualExpr(lhs, rhs):
            x = _evaluate_number(lhs)
            y = _evaluate_number(rhs)
            return x >= y
        # Equality
        case EqualEqualExpr(lhs, rhs):
            x = evaluate_expression(lhs)
            y = evaluate_expression(rhs)
            if type(x) is not type(y):
                raise TypeError(f"Cannot compare {type(x)} and {type(y)}", expr.diag)
            return x == y
        case NotEqualExpr(lhs, rhs):
            x = evaluate_expression(lhs)
            y = evaluate_expression(rhs)
            if type(x) is not type(y):
                raise TypeError(f"Cannot compare {type(x)} and {type(y)}", expr.diag)
            return x != y
