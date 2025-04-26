from collections import deque
from typing import Deque
from typing import Iterator
from char_generator import char_generator, ReadCharState, Diagnostics
from buffered_iterator import BufferedIterator


class CharReader:
    """
    A two-character buffered reader to read characters from successive lines.
    Offers a peek() functionality for lookahead, with a configurable buffer
    length, depending on how much lookahead is needed.
    """

    _BUFSIZE = 2

    def __init__(self, line_iter: Iterator[str]):
        """
        Creates a new CharReader.

        Arguments:
          line_iter:    An iterator yielding successive lines of input, for
                        example from a file.
          bufsize:      Size of the buffer. The charreader keps reading
                        characters until the buffer is full or the end of the
                        input has been reached. When a character is read from
                        the buffer, the next character is read and appended to
                        the end of the buffer (queue).

        """

        ########################################################################
        # Class state and invariants
        ########################################################################

        # Adds buffering to the given character generator, for peeking etc.
        self._buffer: BufferedIterator[ReadCharState] = BufferedIterator(
            char_generator(line_iter), CharReader._BUFSIZE
        )

        # This stores the diagnostic state of the latest character successfully
        # read from the input. We keep this explicitly to support the case
        # where the end of the input has been reached, the buffer has been
        # emptied, but we still need this info. This is normally for the error
        # "unexpected end of input: …".
        #
        # If this is None, it means we never read any input, i.e., the given
        # input was empty.
        self._last_processed_state: Diagnostics | None = None

    def diagnostic_string(self) -> str:
        """
        Returns a string that indentifies the next character (the character
        returned by peek() or next()), by printing the containing line and an
        arrow that points to the character in the line.

        The main use is that if peek() doesn't return an expected character, you
        can use the string returned by this method in the error message.

        If there are no more characters to return, the method returns the
        diagnostic information for the last read character, so you can use it
        in errors like "unexpected end of input".

        Note that once a character is returned by next(), the diagnostic
        information is lost (unless it was the last character available).
        """
        if self._buffer.has_next():
            return self._buffer.peek(0).diags.diagnostic_string()
        elif self._last_processed_state:
            return self._last_processed_state.next_col().diagnostic_string()
        else:
            return "  (can't determine position, maybe there was no input at all)"

    def next(self) -> str:
        """
        Returns the next character and advances to the next character.
        Raises StopIteration if there are no more characters.
        """
        if not self._buffer.has_next():
            # Empty buffer, nothing to return.
            raise StopIteration

        result = self._buffer.next()
        self._last_processed_state = result.diags
        return result.char

    def has_next(self) -> bool:
        """
        Returns True if there is still a character to read, false otherwise.
        """
        return self._buffer.has_next()

    def can_peek(self, offset=0) -> bool:
        """
        Returns true if it is possible to "peek" offset characters ahead.
        can_peek(0) is equivalent to has_next(). The invariant is that if
        can_peek(offset) is true, then peek(offset) returns a valid value. If
        can_peek(offset) is false, then peek(offset) would throw a
        StopIteration exception.
        """
        return self._buffer.can_peek(offset)

    def peek(self, offset=0) -> str:
        """
        Returns the character that would be returned by a call to next(),
        without advancing. Raises StopIteration if there is no more character
        to read.
        """
        return self._buffer.peek(offset).char

    def eat(self, c: str) -> bool:
        """
        If the next character that would be returned by next() matches c,
        this function consumes it and returns true. Otherwise, it returns false and does not consume
        anything.

        If has_next() would return False, eat() returns False().

        This is just an ergonomic improvement so that one doesn't have to
        always first call peek() and then next().
        """
        if len(c) != 1:
            raise ValueError(f"eat() requires exactly one character. Found: {c}")
        if not self._buffer.has_next():
            return False

        if self.peek() == c:
            self.next()
            return True

        return False
