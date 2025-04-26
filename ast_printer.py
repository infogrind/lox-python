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
        case Mult(lhs, rhs):
            return _print_binary_expression("*", lhs, rhs)
        case Div(lhs, rhs):
            return _print_binary_expression("/", lhs, rhs)
        case Negative(expr):
            return f"( - {_print_expression(expr)} )"
        case LogicalNot(expr):
            return f"( ! {_print_expression(expr)} )"
        case _:
            raise RuntimeError(f"Unknown expression: {e}")


def print_program(p: Program) -> str:
    if p.expr:
        return _print_expression(p.expr)
    else:
        # Empty program
        return ""
