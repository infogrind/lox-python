from typing import Iterator, List

from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from charreader import CharReader
from expression_evaluator import VariableError, evaluate_expression
from parser import parse_program
from syntax import Assignment, Expression, PrintStmt, Statement, VarDecl
from token_generator import token_generator


class Interpreter:
    def __init__(self):
        self._vars: dict[str, bool | float | None] = {}

    def _interpret_statement(self, stmt: Statement) -> None:
        match stmt:
            case PrintStmt(expr):
                print(evaluate_expression(expr, self._vars))
            case VarDecl(name, None):
                self._vars[name] = None
            case VarDecl(name, value):
                assert value is not None  # Satisfy the linter.
                self._vars[name] = evaluate_expression(value)
            case Assignment(target, expr):
                if target not in self._vars:
                    raise VariableError(f"Variable {target} not declared", stmt.diag)
                self._vars[target] = None if expr is None else evaluate_expression(expr)
            case Expression():
                # Expressions have no effect, except that they can cause an error, so
                # we always evaluate them.
                evaluate_expression(stmt)

    def interpret(self, code: Iterator[str] | List[str] | str):
        if isinstance(code, str):
            code = iter([code])
        elif isinstance(code, List):
            code = iter(code)
        p = parse_program(
            BufferedScanner(BufferedIterator(token_generator(CharReader(code))))
        )
        for stmt in p.stmts:
            self._interpret_statement(stmt)
