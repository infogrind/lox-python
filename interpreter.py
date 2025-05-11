from typing import Iterator, List

from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from charreader import CharReader
from expression_evaluator import evaluate_expression
from parser import parse_program
from syntax import Declaration, ExprStmt, PrintStmt, Statement, VarDecl
from token_generator import token_generator


class Interpreter:
    def __init__(self):
        self._vars: dict[str, bool | float | None] = {}

    def _interpret_statement(self, stmt: Statement) -> None:
        match stmt:
            case PrintStmt(expr):
                print(evaluate_expression(expr, self._vars))
            case ExprStmt(expr):
                evaluate_expression(expr, self._vars)

    def _interpret_declaration(self, decl: Declaration) -> None:
        match decl:
            case VarDecl(name, None):
                self._vars[name] = None
            case VarDecl(name, value):
                assert value is not None  # Satisfy the linter.
                self._vars[name] = evaluate_expression(value)
            case Statement():
                self._interpret_statement(decl)

    def interpret(self, code: Iterator[str] | List[str] | str):
        if isinstance(code, str):
            code = iter([code])
        elif isinstance(code, List):
            code = iter(code)
        p = parse_program(
            BufferedScanner(BufferedIterator(token_generator(CharReader(code))))
        )
        for decl in p.decls:
            self._interpret_declaration(decl)
