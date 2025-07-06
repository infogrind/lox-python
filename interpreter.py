from typing import Iterator, List

from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from charreader import CharReader
from expression_evaluator import evaluate_expression
from parser import parse_program
from syntax import (
    BlockStmt,
    Declaration,
    ExprStmt,
    IfStmt,
    PrintStmt,
    Statement,
    VarDecl,
)
from token_generator import token_generator


class ScopedVars:
    def __init__(self, interpreter: "Interpreter"):
        self._interpreter = interpreter

    def __contains__(self, name: str) -> bool:
        try:
            self._interpreter._get_variable(name)
            return True
        except KeyError:
            return False

    def __getitem__(self, name: str) -> bool | float | str | None:
        try:
            return self._interpreter._get_variable(name)
        except KeyError:
            raise KeyError(name)

    def __setitem__(self, name: str, value: bool | float | str | None) -> None:
        try:
            self._interpreter._set_variable(name, value)
        except KeyError:
            # If variable doesn't exist, declare it in current scope
            self._interpreter._declare_variable(name, value)


class Interpreter:
    def __init__(self):
        self._scopes: List[dict[str, bool | float | str | None]] = [{}]
        self._scoped_vars = ScopedVars(self)

    def _get_current_scope(self) -> dict[str, bool | float | str | None]:
        return self._scopes[-1]

    def _push_scope(self) -> None:
        self._scopes.append({})

    def _pop_scope(self) -> None:
        self._scopes.pop()

    def _get_variable(self, name: str) -> bool | float | str | None:
        # Look up the variable in scopes from innermost to outermost
        for scope in reversed(self._scopes):
            if name in scope:
                return scope[name]
        # If not found in any scope, raise error (this will be handled by expression_evaluator)
        raise KeyError(name)

    def _set_variable(self, name: str, value: bool | float | str | None) -> None:
        # Look for the variable in scopes from innermost to outermost
        for scope in reversed(self._scopes):
            if name in scope:
                scope[name] = value
                return
        # If not found in any scope, raise error
        raise KeyError(name)

    def _declare_variable(self, name: str, value: bool | float | str | None) -> None:
        # Declare variable in current scope
        self._get_current_scope()[name] = value

    def _interpret_statement(self, stmt: Statement) -> None:
        match stmt:
            case PrintStmt(expr):
                print(evaluate_expression(expr, self._scoped_vars))
            case ExprStmt(expr):
                evaluate_expression(expr, self._scoped_vars)
            case BlockStmt(declarations):
                self._push_scope()
                try:
                    for decl in declarations:
                        self._interpret_declaration(decl)
                finally:
                    self._pop_scope()
            case IfStmt(condition, then_branch, else_branch):
                value = evaluate_expression(condition, self._scoped_vars)
                is_truthy = value is not None and value is not False
                if is_truthy:
                    self._interpret_statement(then_branch)
                elif else_branch:
                    self._interpret_statement(else_branch)

    def _interpret_declaration(self, decl: Declaration) -> None:
        match decl:
            case VarDecl(name, None):
                self._declare_variable(name, None)
            case VarDecl(name, value):
                assert value is not None  # Satisfy the linter.
                self._declare_variable(
                    name, evaluate_expression(value, self._scoped_vars)
                )
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
