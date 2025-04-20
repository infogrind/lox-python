from collections import deque
from typing import Iterator
from typing import Deque


class BufferedIterator[T]:
    """
    Wraps an arbitrary iterator and loads the elements at the front in a buffer
    of size bufsize. This allows peeking at the bufsize first elements, which is
    not possible with a normal iterator.

    If calling next() on the underlying iterator raises an exception, that exception
    is only raised to the user of BufferedIterator when the corresponding element
    would be returned from the buffer, either by next(), peek(), or eat().
    """

    def __init__(self, iter: Iterator[T], bufsize: int = 1):
        self._iter = iter
        self._bufsize = bufsize
        self._buffer: Deque[T | Exception] = deque()

        self._refill_buffer()

    def _refill_buffer(self) -> None:
        """
        Loads elements from the iterator until the buffer is at the desired
        size, or until the end of the input has been reached.
        """
        while len(self._buffer) < self._bufsize:
            try:
                self._buffer.append(next(self._iter))
            except StopIteration:
                # End of input
                return
            except Exception as e:
                # Exceptions are added to the buffer, to be thrown in
                # next() or peek().
                self._buffer.append(e)

    def has_next(self) -> bool:
        """
        Returns True if there is still an element available to return with next(),
        False otherwise.
        """
        return bool(self._buffer)

    def next(self) -> T:
        """
        Returns the next element. Raises StopIteration if no more elements are available.
        """
        if not self._buffer:
            raise StopIteration

        result = self._buffer.popleft()
        self._refill_buffer()

        match result:
            case Exception():
                raise result
            case x:
                return x

    def can_peek(self, pos: int = 0) -> bool:
        """
        Returns True if there are enough elements in the buffer to peek at position pos,
        i.e., if the buffer contains at least pos + 1 elements.

        This should be called before calling peek(), to ensure a peekable element is present.
        """
        if pos < 0:
            raise ValueError(f"Invalid position: {pos}.")
        if pos >= self._bufsize:
            raise ValueError(
                f"Invalid position: {pos}. It must be less than the buffer size {self._bufsize}."
            )
        return pos < len(self._buffer)

    def peek(self, pos: int = 0) -> T:
        """
        Allows to peek at the elements at the head of the iterator. Raises
        StopIteration if there are not enough elements in the buffer. The
        optional parameter pos must be a valid index into the buffer, i.e., it
        must be smaller than bufsize.
        """
        if pos < 0:
            raise ValueError(f"Invalid position: {pos}.")
        if pos >= self._bufsize:
            raise ValueError(
                f"In valid position: {pos}. It must be less than the buffer size {self._bufsize}."
            )
        if pos >= len(self._buffer):
            raise StopIteration

        result = self._buffer[pos]
        match result:
            case Exception():
                raise result
            case x:
                return x

    def eat(self, val: T) -> bool:
        """
        If the character at the head of the iterator is equal to val, advances
        the iterator (consuming the element) and returns True. Otherwise, returns
        false and leaves the iterator state unchanged.

        If there are no more elements, eat() also returns False.

        This is an ergonomic improvement. Instead of writing
          if b.has_next() and b.peek() == "x":
            b.next()
            ...

        one can write
          if b.eat("x"):
            ...
        """
        if not self._buffer:
            return False

        if self.peek(0) == val:
            self.next()
            return True

        return False
