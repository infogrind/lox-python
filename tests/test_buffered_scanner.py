import unittest
from tokens import LPAREN, STRING, RBRACE
from buffered_scanner import BufferedScanner


class TestBufferedScanner(unittest.TestCase):
    def test_empty_buffer_has_no_next(self):
        bs = BufferedScanner(iter([]))
        self.assertFalse(bs.has_next())

    def test_peek_empty_buffer_raises_exception(self):
        bs = BufferedScanner(iter([]))
        with self.assertRaises(StopIteration):
            bs.peek()

    def test_next_on_empty_buffer_raises_exception(self):
        bs = BufferedScanner(iter([]))
        with self.assertRaises(StopIteration):
            bs.next()

    def test_single_element(self):
        bs = BufferedScanner(iter([LPAREN()]))
        self.assertTrue(bs.has_next())
        self.assertEqual(bs.peek(), LPAREN())
        self.assertEqual(bs.next(), LPAREN())
        self.assertFalse(bs.has_next())

    def test_longer_sequence(self):
        bs = BufferedScanner(
            iter([LPAREN(), LPAREN(), STRING("foo"), RBRACE(), RBRACE()])
        )
        self.assertTrue(bs.peek(), LPAREN())
        self.assertTrue(bs.next(), LPAREN())
        self.assertTrue(bs.peek(), LPAREN())
        self.assertTrue(bs.next(), LPAREN())
        self.assertTrue(bs.peek(), STRING("foo"))
        self.assertTrue(bs.next(), STRING("foo"))
        self.assertTrue(bs.peek(), RBRACE())
        self.assertTrue(bs.next(), RBRACE())
        self.assertTrue(bs.peek(), RBRACE())
        self.assertTrue(bs.next(), RBRACE())
        self.assertFalse(bs.has_next())

    def test_error_only_raised_on_next(self):
        """
        The buffered reader should store any exceptions that the underlying
        iterator raises internally, and only raise them when next() is called
        for the actual value.
        """

        def _error_generator():
            yield LPAREN()
            raise RuntimeError("foo")

        bs = BufferedScanner(_error_generator())
        self.assertEqual(bs.next(), LPAREN())
        with self.assertRaises(RuntimeError) as context:
            bs.next()
        self.assertEqual(str(context.exception), "foo")
