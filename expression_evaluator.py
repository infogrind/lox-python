from syntax import (
    Program,
    Expression,
    Number,
    String,
    Negative,
    LogicalNot,
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


class TypeError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def _assert_numbers(msg: str, *args) -> None:
    for a in args:
        if not isinstance(a, float):
            raise TypeError(msg)


def _assert_bool(msg: str, *args) -> None:
    for a in args:
        if not isinstance(a, bool):
            raise TypeError(msg)


def _evaluate_number(expr: Expression) -> float:
    x = evaluate_expression(expr)
    if not isinstance(x, float):
        raise TypeError("Expected: number")
    return x


def _evaluate_bool(expr: Expression) -> bool:
    x = evaluate_expression(expr)
    if not isinstance(x, bool):
        raise TypeError("Expected: bool")
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
                raise TypeError(f"Cannot compare {type(x)} and {type(x)}")
            return x == y
        case NotEqualExpr(lhs, rhs):
            x = evaluate_expression(lhs)
            y = evaluate_expression(rhs)
            if type(x) is not type(y):
                raise TypeError(f"Cannot compare {type(x)} and {type(x)}")
            return x != y
