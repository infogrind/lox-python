import unittest
from charreader import CharReader


class TestCharReader(unittest.TestCase):
    def test_can_iterate_through_single_line(self):
        c = CharReader(iter(["Hello\n"]))

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "H")
        self.assertEqual(c.next(), "H")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "e")
        self.assertEqual(c.next(), "e")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "l")
        self.assertEqual(c.next(), "l")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "l")
        self.assertEqual(c.next(), "l")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "o")
        self.assertEqual(c.next(), "o")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "\n")
        self.assertEqual(c.next(), "\n")

        self.assertFalse(c.has_next())

    def test_can_iterate_through_multiple_lines(self):
        c = CharReader(iter(["Hello\n", "World\n"]))

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "H")
        self.assertEqual(c.next(), "H")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "e")
        self.assertEqual(c.next(), "e")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "l")
        self.assertEqual(c.next(), "l")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "l")
        self.assertEqual(c.next(), "l")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "o")
        self.assertEqual(c.next(), "o")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "\n")
        self.assertEqual(c.next(), "\n")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "W")
        self.assertEqual(c.next(), "W")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "o")
        self.assertEqual(c.next(), "o")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "r")
        self.assertEqual(c.next(), "r")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "l")
        self.assertEqual(c.next(), "l")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "d")
        self.assertEqual(c.next(), "d")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(), "\n")
        self.assertEqual(c.next(), "\n")

        self.assertFalse(c.has_next())

    def test_empty_lines_are_skipped(self):
        c = CharReader(iter(["", "", "a", "", "b"]))
        self.assertEqual(c.next(), "a")
        self.assertEqual(c.next(), "b")
        self.assertFalse(c.has_next())

    def test_call_next_at_end_raises_stop_iteration(self):
        c = CharReader(iter(["ab"]))
        c.next()
        c.next()
        self.assertRaises(StopIteration, c.next)

    def test_empty_line_iterator(self):
        c = CharReader(iter([]))
        self.assertFalse(c.has_next())

    def test_diagnostic_message(self):
        c = CharReader(iter(["a bc x"]))
        self.assertEqual(
            c.diagnostic_string(),
            """\
    1: a bc x
       ^
       ┗--- here\
""",
        )

        c.next()
        c.next()

        self.assertEqual(
            c.diagnostic_string(),
            """\
    1: a bc x
         ^
         ┗--- here\
""",
        )

    def test_diagnostic_message_long_buffer(self):
        c = CharReader(iter(["a bc x"]))
        self.assertEqual(
            c.diagnostic_string(),
            """\
    1: a bc x
       ^
       ┗--- here\
""",
        )

        c.next()
        c.next()

        self.assertEqual(
            c.diagnostic_string(),
            """\
    1: a bc x
         ^
         ┗--- here\
""",
        )

    def test_diagnostic_message_newlines(self):
        c = CharReader(iter(["a\n", "  b\n"]))

        # Eat everything up to but excluding b (the newlines are read as
        # individual characters).
        c.next()
        c.next()
        c.next()
        c.next()

        self.assertEqual(
            c.diagnostic_string(),
            """\
    2:   b
         ^
         ┗--- here""",
        )

    def test_diagnostic_message_col_remains_at_last_char(self):
        # Note that 'b' is the last character. If we call next() again, the diagnostic
        # message should still point at b.
        c = CharReader(iter(["a\n", "  b"]))

        # Eat everything up to and including b.
        c.next()
        c.next()
        c.next()
        c.next()

        # The diagnistic message should still point at b.
        self.assertEqual(
            c.diagnostic_string(),
            """\
    2:   b
         ^
         ┗--- here""",
        )

    def test_longer_buffer_peek_and_next_single_line(self):
        c = CharReader(iter(["Hello\n"]))

        self.assertTrue(c.has_next())
        self.assertTrue(c.can_peek((0)))
        self.assertTrue(c.can_peek((1)))
        self.assertEqual(c.peek(0), "H")
        self.assertEqual(c.peek(1), "e")
        self.assertEqual(c.next(), "H")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(0), "e")
        self.assertEqual(c.peek(1), "l")
        self.assertEqual(c.next(), "e")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(0), "l")
        self.assertEqual(c.peek(1), "l")
        self.assertEqual(c.next(), "l")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(0), "l")
        self.assertEqual(c.peek(1), "o")
        self.assertEqual(c.next(), "l")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(0), "o")
        self.assertEqual(c.peek(1), "\n")
        self.assertEqual(c.next(), "o")

        self.assertTrue(c.has_next())
        self.assertEqual(c.peek(0), "\n")

        # Peeking further than allowed.
        self.assertFalse(c.can_peek(1))
        with self.assertRaises(StopIteration):
            c.peek(1)
        self.assertEqual(c.next(), "\n")

        self.assertFalse(c.has_next())

    def test_offsets_with_empty_input(self):
        c = CharReader(iter([""]))
        self.assertFalse(c.has_next())
        self.assertFalse(c.can_peek(0))

    def test_multiple_lines_in_input(self):
        c = CharReader(iter(["ab", "c\n", "\n", "", "x"]))
        self.assertEqual(c.peek(0), "a")
        c.next()  # consume b
        c.next()  # consume c
        self.assertEqual(c.peek(1), "\n")

    def test_invalid_peek_value(self):
        c = CharReader(iter(["asdf"]))
        with self.assertRaises(ValueError):
            c.can_peek(-1)
        with self.assertRaises(ValueError):
            c.can_peek(-10)
        with self.assertRaises(ValueError):
            c.peek(-1)
        with self.assertRaises(ValueError):
            c.peek(-10)

    def test_eat(self):
        c = CharReader(iter(["asdf"]))
        self.assertTrue(c.eat("a"))
        self.assertTrue(c.eat("s"))
        self.assertFalse(c.eat("x"))
        self.assertTrue(c.eat("d"))
        self.assertTrue(c.eat("f"))
        self.assertFalse(c.eat("x"))
