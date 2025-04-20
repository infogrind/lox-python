from collections.abc import Buffer
import unittest
from buffered_iterator import BufferedIterator


class TestBufferedIterator(unittest.TestCase):
    def test_empty_iterator_has_no_next(self):
        b = BufferedIterator(iter([]), 1)
        self.assertFalse(b.has_next())

    def test_empty_iterator_cannot_peek(self):
        b = BufferedIterator(iter([]), 1)
        self.assertFalse(b.can_peek())
        self.assertFalse(b.can_peek(0))

    def test_index_greater_than_bufsize(self):
        b = BufferedIterator(iter([]), 1)
        with self.assertRaises(ValueError):
            b.can_peek(1)

        b = BufferedIterator(iter([]), 2)
        with self.assertRaises(ValueError):
            b.can_peek(2)

    def test_advance_through_single_element_buffer(self):
        b = BufferedIterator(iter([1, 2, 3]), 1)
        self.assertTrue(b.has_next())
        self.assertEqual(b.next(), 1)

        self.assertTrue(b.has_next())
        self.assertEqual(b.next(), 2)

        self.assertTrue(b.has_next())
        self.assertEqual(b.next(), 3)

        self.assertFalse(b.has_next())

    def test_advance_through_multi_element_buffer(self):
        b = BufferedIterator(iter([1, 2, 3]), 10)
        self.assertTrue(b.has_next())
        self.assertEqual(b.next(), 1)

        self.assertTrue(b.has_next())
        self.assertEqual(b.next(), 2)

        self.assertTrue(b.has_next())
        self.assertEqual(b.next(), 3)

        self.assertFalse(b.has_next())

    def test_peek_and_eat(self):
        b = BufferedIterator(iter([1, 2, 3]), 2)

        self.assertTrue(b.can_peek(0))
        self.assertEqual(b.peek(0), 1)

        self.assertTrue(b.can_peek(1))
        self.assertEqual(b.peek(1), 2)

        self.assertTrue(b.eat(1))
        self.assertTrue(b.eat(2))
        self.assertFalse(b.eat(4))

        with self.assertRaises(StopIteration):
            b.peek(1)

        self.assertTrue(b.eat(3))

        self.assertFalse(b.eat(4))

    def test_raises_exception_at_right_point(self):
        def exception_generator():
            yield 1
            raise Exception("foo")

        b = BufferedIterator(exception_generator(), 1)

        self.assertEqual(b.next(), 1)

        self.assertTrue(b.can_peek(0))
        with self.assertRaises(Exception) as context:
            b.peek()
        self.assertEqual(str(context.exception), "foo")

        with self.assertRaises(Exception) as context:
            b.next()
        self.assertEqual(str(context.exception), "foo")
