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
    return f"( {op} {_print_expression(lhs)} {_print_expression(rhs)} )"


def _print_expression(e: Expression) -> str:
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
        case Add(lhs, rhs):
            return _print_binary_expression("+", lhs, rhs)
        case Subtract(lhs, rhs):
            return _print_binary_expression("-", lhs, rhs)
        case _:
            raise RuntimeError(f"Unknown expression: {e}")


def print_node(n: Node) -> str:
    match n:
        case Expression():
            return _print_expression(n)
        case _:
            raise RuntimeError(f"Unexpected node type: {n}")
