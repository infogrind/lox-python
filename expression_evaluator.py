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
    String,
    Subtract,
    TrueExpr,
    Variable,
)


class TypeError(Exception):
    def __init__(self, message: str, diag: Diagnostics):
        super().__init__(message)
        self.message: str = message
        self.diagnostics: Diagnostics = diag


class VariableError(Exception):
    def __init__(self, message: str, diag: Diagnostics):
        super().__init__(message)
        self.message: str = message
        self.diagnostics: Diagnostics = diag


def _evaluate_number(expr: Expression, vars) -> float:
    x = evaluate_expression(expr, vars)
    if not isinstance(x, float):
        raise TypeError("Expected: number", expr.diag)
    return x


def _evaluate_bool(expr: Expression, vars) -> bool:
    x = evaluate_expression(expr, vars)
    if not isinstance(x, bool):
        raise TypeError("Expected: bool", expr.diag)
    return x


def evaluate_expression(expr: Expression, vars={}) -> float | bool | str | None:
    match expr:
        # Primaries
        case Number(v):
            return v
        case String(v):
            return v
        case TrueExpr():
            return True
        case FalseExpr():
            return False
        case Nil():
            return None
        case Variable(name):
            if name not in vars:
                raise VariableError(f"'{name}' not defined", expr.diag)
            return vars[name]
        case Grouping(expr):
            return evaluate_expression(expr, vars)
        # Unary
        case Negative(expr):
            x = _evaluate_number(expr, vars)
            return -x
        case LogicalNot(expr):
            x = _evaluate_bool(expr, vars)
            return not x
        # Factors
        case Mult(lhs, rhs):
            x = _evaluate_number(lhs, vars)
            y = _evaluate_number(rhs, vars)
            return x * y
        case Div(lhs, rhs):
            x = _evaluate_number(lhs, vars)
            y = _evaluate_number(rhs, vars)
            return x / y
        # Terms
        case Add(lhs, rhs):
            x = _evaluate_number(lhs, vars)
            y = _evaluate_number(rhs, vars)
            return x + y
        case Subtract(lhs, rhs):
            x = _evaluate_number(lhs, vars)
            y = _evaluate_number(rhs, vars)
            return x - y
        # Comparisons
        case LessThanExpr(lhs, rhs):
            x = _evaluate_number(lhs, vars)
            y = _evaluate_number(rhs, vars)
            return x < y
        case LessEqualExpr(lhs, rhs):
            x = _evaluate_number(lhs, vars)
            y = _evaluate_number(rhs, vars)
            return x <= y
        case GreaterThanExpr(lhs, rhs):
            x = _evaluate_number(lhs, vars)
            y = _evaluate_number(rhs, vars)
            return x > y
        case GreaterEqualExpr(lhs, rhs):
            x = _evaluate_number(lhs, vars)
            y = _evaluate_number(rhs, vars)
            return x >= y
        # Equality
        case EqualEqualExpr(lhs, rhs):
            x = evaluate_expression(lhs, vars)
            y = evaluate_expression(rhs, vars)
            if type(x) is not type(y):
                raise TypeError(f"Cannot compare {type(x)} and {type(y)}", expr.diag)
            return x == y
        case NotEqualExpr(lhs, rhs):
            x = evaluate_expression(lhs, vars)
            y = evaluate_expression(rhs, vars)
            if type(x) is not type(y):
                raise TypeError(f"Cannot compare {type(x)} and {type(y)}", expr.diag)
            return x != y
        case Assignment(target, expr):
            if target not in vars:
                raise VariableError(
                    f"Variable {target} not declared (vars: {repr(vars)})", expr.diag
                )
            vars[target] = evaluate_expression(expr, vars)
            return vars[target]
        case _:
            raise RuntimeError(f"Don't know how to evaluate expression {repr(expr)}")
