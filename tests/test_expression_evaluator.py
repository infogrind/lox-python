import unittest

from buffered_iterator import BufferedIterator
from buffered_scanner import BufferedScanner
from charreader import CharReader
from diagnostics import Pos
from expression_evaluator import TypeError, evaluate_expression
from parser import parse_expression
from syntax import Expression
from token_generator import token_generator


def _parse_string(s: str) -> Expression:
    return parse_expression(
        BufferedScanner(BufferedIterator(token_generator(CharReader(iter([s]))), 2))
    )


class ExpressionEvaluatorTest(unittest.TestCase):
    # Literals only

    def _evaluate(self, s: str, vars={}):
        expr = _parse_string(s)
        return evaluate_expression(expr, vars)

    def assertEvaluates(self, s: str, v: bool | float | None, vars={}):
        self.assertEqual(
            self._evaluate(s, vars), v, "Evaluation doesn't match expected value"
        )

    def test_evaluate_booleans(self):
        self.assertEvaluates("true", True)
        self.assertEvaluates("false", False)

    def test_evaluate_numbers(self):
        self.assertEvaluates("1.2", 1.2)

    def test_evaluate_nil(self):
        self.assertEvaluates("nil", None)

    def test_evaluate_negation(self):
        self.assertEvaluates("-4", -4.0)
        self.assertEvaluates("----4", 4.0)

    def test_evaluate_negation_type_error(self):
        with self.assertRaises(TypeError):
            self._evaluate("-true")
        with self.assertRaises(TypeError):
            self._evaluate("-nil")

    def test_evaluate_logical_not(self):
        self.assertEvaluates("!true", False)
        self.assertEvaluates("!false", True)
        self.assertEvaluates("!!true", True)
        self.assertEvaluates("!!false", False)
        self.assertEvaluates("!!!true", False)
        self.assertEvaluates("!!!false", True)

    def test_evaluate_logical_not_type_error(self):
        with self.assertRaises(TypeError):
            self._evaluate("!3.2")
        with self.assertRaises(TypeError):
            self._evaluate("!nil")

    def test_evaluate_multiplication(self):
        self.assertEvaluates("2 * 3", 6.0)
        self.assertEvaluates("4 * -2.1", -8.4)

    def test_evaluate_multiplication_type_error(self):
        with self.assertRaises(TypeError):
            self._evaluate("2 * true")
        with self.assertRaises(TypeError):
            self._evaluate("true * 2")
        with self.assertRaises(TypeError):
            self._evaluate("true * false")
        with self.assertRaises(TypeError):
            self._evaluate("2.3 * nil")

    def test_evaluate_division(self):
        self.assertEvaluates("3/2", 1.5)
        self.assertEvaluates("10/-4", -2.5)

    def test_evaluate_division_type_error(self):
        with self.assertRaises(TypeError):
            self._evaluate("3/true")
        with self.assertRaises(TypeError):
            self._evaluate("3/nil")
        with self.assertRaises(TypeError):
            self._evaluate("false/true")
        with self.assertRaises(TypeError):
            self._evaluate("nil/2")

    def test_evaluate_addition(self):
        self.assertEvaluates("1 + 2", 3.0)

    def test_evaluate_subtraction(self):
        self.assertEvaluates("1 - 2", -1.0)

    def test_evaluate_bool_number_addition(self):
        with self.assertRaises(TypeError):
            self._evaluate("1 + true")

    def test_evaluate_bool_number_subtration(self):
        with self.assertRaises(TypeError):
            self._evaluate("false - 1")

    def test_evaluate_less_than(self):
        self.assertEvaluates("2 < 3", True)
        self.assertEvaluates("2 < -3", False)
        self.assertEvaluates("3 < 2", False)
        self.assertEvaluates("2 < 2", False)

    def test_evaluate_less_equal(self):
        self.assertEvaluates("2 <= 3", True)
        self.assertEvaluates("2 <= -3", False)
        self.assertEvaluates("3 <= 2", False)
        self.assertEvaluates("2 <= 2", True)

    def test_evaluate_greater_than(self):
        self.assertEvaluates("2 > 3", False)
        self.assertEvaluates("2 > -3", True)
        self.assertEvaluates("3 > 2", True)
        self.assertEvaluates("2 > 2", False)

    def test_evaluate_greater_equal(self):
        self.assertEvaluates("2 >= 3", False)
        self.assertEvaluates("2 >= -3", True)
        self.assertEvaluates("3 >= 2", True)
        self.assertEvaluates("2 >= 2", True)

    def test_equal_equal_number(self):
        self.assertEvaluates("1 == 1", True)
        self.assertEvaluates("1 == 2", False)

    def test_equal_equal_bool(self):
        self.assertEvaluates("true == true", True)
        self.assertEvaluates("false == false", True)
        self.assertEvaluates("true == false", False)

    def test_equal_equal_nil(self):
        self.assertEvaluates("nil == nil", True)

    def test_equal_equal_type_error(self):
        with self.assertRaises(TypeError):
            self._evaluate("true == 1")
        with self.assertRaises(TypeError):
            self._evaluate("true == nil")
        with self.assertRaises(TypeError):
            self._evaluate("nil == 1")

    def test_not_equal_number(self):
        self.assertEvaluates("1 != 1", False)
        self.assertEvaluates("1 != 2", True)

    def test_not_equal_bool(self):
        self.assertEvaluates("true != false", True)
        self.assertEvaluates("true != true", False)

    def test_not_equal_nil(self):
        self.assertEvaluates("nil != nil", False)

    def test_not_equal_type_error(self):
        with self.assertRaises(TypeError) as ctx:
            self._evaluate("3 != true")
        self.assertEqual(ctx.exception.diagnostics.pos, Pos(1, 3))

        with self.assertRaises(TypeError) as ctx:
            self._evaluate("3 != nil")
        self.assertEqual(ctx.exception.diagnostics.pos, Pos(1, 3))

        with self.assertRaises(TypeError) as ctx:
            self._evaluate("nil != true")
        self.assertEqual(ctx.exception.diagnostics.pos, Pos(1, 5))

    def test_error_position_in_complex_expressions(self):
        with self.assertRaises(TypeError) as ctx:
            # Comparison of incompatible types shoudl be at the == position.
            self._evaluate("true == ((1 + 2) * 3)")
        self.assertEqual(ctx.exception.diagnostics.pos, Pos(1, 6))

        with self.assertRaises(TypeError) as ctx:
            # Expected type of operand should be at the first parenthesis.
            self._evaluate("1 + ((true != false) == !false)")
        self.assertEqual(ctx.exception.diagnostics.pos, Pos(1, 5))

    def test_complex_expressions(self):
        self.assertEvaluates("4 + 7*8/ 93 > 4.60", True)
        self.assertEvaluates("4 + 7*8/ 93 < 4.61", True)
        self.assertEvaluates("(2 * 3) > 5 == 8 - 4*3 < -3", True)
        self.assertEvaluates("(!true == true) == (!false == false)", True)
        self.assertEvaluates("(!true == false) == (!false == false)", False)

    # Assignment expressions

    def test_simple_assignment(self):
        self.assertEvaluates("a = 2", 2.0, {"a": None})

    def test_nested_assignment(self):
        self.assertEvaluates(
            "a = 2 + (b = 3 + (c = 4))", 9.0, {"a": None, "b": None, "c": None}
        )

    # Expressions with variables

    def test_evaluate_single_numeric_variable(self):
        self.assertEvaluates("a", 3.0, {"a": 3.0})

    def test_evaluate_single_bool_variable(self):
        self.assertEvaluates("b", True, {"b": True})

    def test_evaluate_add_variables(self):
        self.assertEvaluates("c + d", 27.0, {"c": 18.0, "d": 9.0})
