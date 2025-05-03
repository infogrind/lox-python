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
    PrintStmt,
    Program,
    Statement,
    String,
    Subtract,
    TrueExpr,
    VarDecl,
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
        case Grouping(expr):
            return _print_expression(expr)
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


def _print_statement(s: Statement):
    match s:
        case PrintStmt(expr):
            return f"( print {_print_expression(expr)} )"
        case VarDecl(name, expr):
            if expr:
                return f"( var {name} {_print_expression(expr)} )"
            else:
                return f"( var {name} )"
        case Expression():
            return _print_expression(s)
        case _:
            raise RuntimeError(f"Unknown program type: {s}")


def print_program(p: Program) -> str:
    return "".join([f"{_print_statement(s)}; " for s in p.stmts]).rstrip()
