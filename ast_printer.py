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
        case Variable(name):
            return name
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
        case LogicalAnd(lhs, rhs):
            return _print_binary_expression("and", lhs, rhs)
        case LogicalOr(lhs, rhs):
            return _print_binary_expression("or", lhs, rhs)
        case Negative(expr):
            return f"( - {_print_expression(expr)} )"
        case LogicalNot(expr):
            return f"( ! {_print_expression(expr)} )"
        case Assignment(target, expr):
            return f"( = {target} {_print_expression(expr)} )"
        case _:
            raise RuntimeError(f"Unknown expression: {e}")


def _print_statement(s: Statement):
    match s:
        case PrintStmt(expr):
            return f"( print {_print_expression(expr)} )"
        case ExprStmt(expr):
            return _print_expression(expr)
        case BlockStmt(declarations):
            if declarations:
                inner = " ".join([f"{_print_declaration(d)};" for d in declarations])
                return f"{{ {inner} }}"
            else:
                return "{ }"
        case IfStmt(condition, then_branch, else_branch):
            if else_branch:
                return f"( if {_print_expression(condition)} {_print_statement(then_branch)} else {_print_statement(else_branch)} )"
            else:
                return f"( if {_print_expression(condition)} {_print_statement(then_branch)} )"
        case _:
            raise RuntimeError(f"Unknown statement type: {s}")


def _print_declaration(d: Declaration) -> str:
    match d:
        case VarDecl(name, expr):
            if expr:
                return f"( var {name} {_print_expression(expr)} )"
            else:
                return f"( var {name} )"
        case Statement():
            return _print_statement(d)
        case _:
            raise RuntimeError("Unknown declaration type: {d}")


def print_program(p: Program) -> str:
    return "\n".join([f"{_print_declaration(d)}" for d in p.decls]).rstrip()
