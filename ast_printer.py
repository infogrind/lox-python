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


def _print_binary_expression(op: str, lhs: Expression, rhs: Expression) -> str:
    return f"( {op} {print_expression(lhs)} {print_expression(rhs)} )"


def print_expression(e: Expression) -> str:
    match e:
        case Number(value):
            return str(value)
        case String(value):
            return value
        case TrueExpr():
            return "true"
        case FalseExpr():
            return "false"
        case Nil():
            return "nil"
        case EqualEqualExpr(lhs, rhs):
            return _print_binary_expression("==", lhs, rhs)
        case NotEqualExpr(lhs, rhs):
            return _print_binary_expression("!=", lhs, rhs)
        case LessThanExpr(lhs, rhs):
            return _print_binary_expression("<", lhs, rhs)
        case LessEqualExpr(lhs, rhs):
            return _print_binary_expression("<=", lhs, rhs)
        case GreaterThanExpr(lhs, rhs):
            return _print_binary_expression(">", lhs, rhs)
        case GreaterEqualExpr(lhs, rhs):
            return _print_binary_expression(">=", lhs, rhs)
        case _:
            raise RuntimeError(f"Unknown expression: {e}")
