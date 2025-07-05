import io
import unittest
from contextlib import contextmanager
from typing import Generator
from unittest.mock import patch

from expression_evaluator import TypeError, VariableError
from interpreter import Interpreter


class TestInterpreter(unittest.TestCase):
    @contextmanager
    def assertOutputs(self, expected: str) -> Generator[None, None, None]:
        """
        Asserts that the provided context outputs the given string to stdout.
        Trailing whitespace is ignored, so that one doesn't have to add a newline
        at the end of `expected` each time.
        """
        with patch("sys.stdout", new=io.StringIO()) as fake_output:
            yield
            self.assertEqual(fake_output.getvalue().rstrip(), expected.rstrip())

    def test_prints_simple_value(self):
        i = Interpreter()
        with self.assertOutputs("3.0"):
            i.interpret("print(3);")

    def test_prints_addition_result(self):
        with self.assertOutputs("7.0"):
            Interpreter().interpret("print(3 + 4);")

    def test_prints_variable_value(self):
        with self.assertOutputs("4.0"):
            Interpreter().interpret(["var a = 4;", "print(a);"])

    def test_undefined_variable(self):
        with self.assertRaises(VariableError) as context:
            Interpreter().interpret("print(a);")

        self.assertEqual(context.exception.message, "'a' not defined")

    def test_redeclare_variable(self):
        with self.assertOutputs("1.0\nTrue"):
            Interpreter().interpret(
                ["var a = 1.0;", "print(a);", "var a = true;", "print(a);"]
            )

    def test_type_error(self):
        with self.assertRaises(TypeError) as context:
            Interpreter().interpret(["var a = nil;", "print(a + 1);"])

        self.assertEqual(context.exception.message, "Expected: number")

    def test_boolean_variable(self):
        with self.assertOutputs("False"):
            Interpreter().interpret(
                [
                    "var b = true;",
                    "print(!b);",
                ]
            )

    def test_interpreter_keeps_state(self):
        i = Interpreter()
        i.interpret("var a = 4 + 7*3;")
        with self.assertOutputs("25.0"):
            i.interpret("print(a);")

    def test_complex_variable_name(self):
        with self.assertOutputs("42.1"):
            Interpreter().interpret(["var _ae_U3 = 42.1;print(_ae_U3);"])

    def test_assignment(self):
        with self.assertOutputs("77.7"):
            Interpreter().interpret(["var foo;", "foo = 77.7;", "print(foo);"])

    def test_reassignment(self):
        with self.assertOutputs("-12.3"):
            Interpreter().interpret(
                ["var x = 5555;", "x = 384.1;", "x = -12.3;", "print(x);"]
            )

    def test_nested_assignment_simple(self):
        i = Interpreter()
        i.interpret(["var x;", "var y;", "x = y = 12.34;"])
        with self.assertOutputs("12.34"):
            i.interpret("print(x);")
        with self.assertOutputs("12.34"):
            i.interpret("print(y);")

    def test_complex_nested_assignment(self):
        i = Interpreter()
        i.interpret(["var x;", "var y;"])
        i.interpret("x = 3 + (y = 4);")
        with self.assertOutputs("7.0"):
            i.interpret("print(x);")
        with self.assertOutputs("4.0"):
            i.interpret("print(y);")

    def test_expr_with_error(self):
        with self.assertRaises(TypeError):
            Interpreter().interpret("3 + true;")

    def test_multi_input_with_type_error(self):
        i = Interpreter()
        i.interpret("var a = 77;")
        with self.assertRaises(TypeError):
            i.interpret("print(true == a);")

    def test_variable_declaration_with_variable_reference(self):
        with self.assertOutputs("10.0"):
            Interpreter().interpret(["var x = 5;", "var y = x + 5;", "print(y);"])

    def test_empty_block(self):
        with self.assertOutputs("42.0"):
            Interpreter().interpret(["var x = 42;", "{}", "print(x);"])

    def test_block_with_statements(self):
        with self.assertOutputs("1.0\n2.0"):
            Interpreter().interpret(
                ["var x = 1;", "{", "  print(x);", "  var y = 2;", "  print(y);", "}"]
            )

    def test_block_scoping(self):
        with self.assertOutputs("inner\nouter"):
            Interpreter().interpret(
                [
                    'var x = "outer";',
                    "{",
                    '  var x = "inner";',
                    "  print(x);",
                    "}",
                    "print(x);",
                ]
            )

    def test_nested_blocks(self):
        with self.assertOutputs("1.0\n2.0\n3.0\n2.0"):
            Interpreter().interpret(
                [
                    "var x = 1;",
                    "{",
                    "  print(x);",
                    "  var x = 2;",
                    "  {",
                    "    print(x);",
                    "    var x = 3;",
                    "    print(x);",
                    "  }",
                    "  print(x);",
                    "}",
                ]
            )
