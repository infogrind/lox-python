from collections import deque
from dataclasses import dataclass, replace
from typing import Deque
from typing import Iterator


@dataclass
class _DiagnosticState:
    """
    Represents the information to diagnose problems related to a specific read
    character: At which line and column it was found, and a string with the
    actual line.

    The invariant is that this is in sync with the buffer, except in these
    cases:
    - If the end of input has been reached, head_char will be None, but the
      diagnostic state will still be that of the previous character.
    - If there was never any input (we started out with an empty input), then
      the diagnostic state is None.
    """

    col_no: int  # The column at which the character was located.
    line_no: int  # Dito for the line.
    line: str | None  # The actual line of input.

    def has_state(self) -> bool:
        return self.line is not None

    def increase_line(self) -> None:
        self.line_no = self.line_no + 1

    def increase_col(self) -> None:
        self.col_no = self.col_no + 1

    def diagnostic_string(self) -> str:
        if self.line is None:
            raise RuntimeError("No diagnostics for uninitialized state.")

        line_prefix = f"{self.line_no:>5}: "
        output = [line_prefix + self.line]
        arrow_indent = " " * len(line_prefix) + " " * (self.col_no - 1)
        output.append(arrow_indent + "^")
        output.append(arrow_indent + "┗--- here")
        return "\n".join(output)


@dataclass
class _ReadCharState:
    """
    Represents a read character with its diagnostic state. This is stored in
    the char reader's buffer.
    """

    char: str
    diags: _DiagnosticState


class CharReader:
    """
    A reader to read characters from successive lines. Offers a peek()
    functionality for lookahead.
    """

    def __init__(self, line_iter: Iterator[str], bufsize: int = 1):
        if bufsize < 1:
            # In theory we could also support an unbuffered version, but that
            # is currently not implemented.
            raise ValueError("Buffer size must be positive, to support peeking.")

        self._line_iter = line_iter
        self._bufsize = bufsize
        self._buffer: Deque[_ReadCharState] = deque()

        # Variables to support the diagnostic state. These always correspond to
        # the last position actually read from the file. Because CharReader
        # does buffering, the diagnostic state of buffered characters are kept
        # in a separate _DiagnosticState object for each buffered character.
        #
        # The invariant is that these variables always match the information of
        # the last character read from the input, except if no character could
        # ever be read (e.g. if the input was empty), in which case they keep
        # their initial values assigned here.
        self._last_processed_state = _DiagnosticState(0, 0, None)

        # Initialize the state: load the first line and the first character.
        self._advance_line()
        self._refill_buffer()

    def _advance_line(self):
        """
        Loads the next non-empty line from the input iterator into head_line, and resets
        the _char_iter.

        If the input iterator has no more elements, head_line is set to none.
        """
        while True:
            try:
                # _head_line is the last line read from the input, or None if
                # the end of lines has been reached. Then each successive
                # character is read from this variable until the end, when the
                # next line is loaded.
                self._head_line = next(self._line_iter)

                # Note that empty lines are not handled in any special way. If
                # the line read was empty, then the next call to _advance_char
                # will just trigger _advance_line again.

                # Reset the iterator that iterates through individual characters.
                self._char_iter = iter(self._head_line)

                # Update the diagnostic information.
                self._last_processed_state.increase_line()
                self._last_processed_state.col_no = 0
                self._last_processed_state.line = self._head_line.rstrip()

            except StopIteration:
                # End of lines reached
                self._head_line = None
                return
            if self._head_line != "":
                # Found next non-empty line.
                break
            # Continue to skip empty lines.

    def _refill_buffer(self) -> None:
        """
        Loads characters from the input until the buffer is again at _bufsize
        or until the end of the input has been reached.
        """
        if len(self._buffer) >= self._bufsize:
            # Nothing to do.
            return
        if self._head_line is None:
            return
        try:
            read_char = next(self._char_iter)
            # End of current line, need to advance.
        except StopIteration:
            self._advance_line()

            # _advance_line either sets the current line to a non-empty one and points the
            # char_iter at the start of it, or sets the line to None. In either case, we can call _advance_char
            # recursively, because we know we won't make another recursive call.
            return self._refill_buffer()

        # We've successfully read a character from the current line, so we can update the state.
        self._last_processed_state.increase_col()
        self._buffer.append(
            _ReadCharState(read_char, replace(self._last_processed_state))
        )

        # Recursively iterate until the buffer is full.
        return self._refill_buffer()

    def line_no(self) -> int:
        """
        Returns the number of the last processed line.
        """
        if self._buffer:
            return self._buffer[0].diags.line_no
        elif self._last_processed_state.has_state():
            return self._last_processed_state.line_no
        else:
            return 0

    def char_no(self) -> int:
        """
        Returns the number of the last processed character in the current line,
        or 0 if no character has been processed (e.g. if the current line is an
        empty line).

        "Processed" means it has actually been read from the input and is
        available to next() or peek().
        """
        if self._buffer:
            return self._buffer[0].diags.col_no
        elif self._last_processed_state.has_state():
            return self._last_processed_state.col_no
        else:
            return 0

    def diagnostic_string(self) -> str:
        """
        Returns a string that indentifies the last character read into head, by
        printing the containing line and an arrow that points to the character in the line.

        If the head character is None, meaning we have returned the last available character,
        the diagnostic information is still for the last character read into head, so you can use
        it in errors like "unexpected end of input".

        Note that once a character is returned by next(), the diagnostic information is lost.
        """
        if self._buffer:
            return self._buffer[0].diags.diagnostic_string()
        elif self._last_processed_state.has_state():
            return self._last_processed_state.diagnostic_string()
        else:
            return "  (can't determine position, maybe there was no input at all)"

    def next(self) -> str:
        """
        Returns the next character and advances to the next character.
        Raises StopIteration if there are no more characters.
        """
        if not self._buffer:
            # Empty buffer, nothing to return.
            raise StopIteration

        result = self._buffer.popleft().char

        # Always keep the buffer full.
        self._refill_buffer()
        return result

    def has_next(self) -> bool:
        """
        Returns True if there is still a character to read, false otherwise.
        """
        return bool(self._buffer)

    def can_peek(self, offset=0) -> bool:
        """
        Returns true if it is possible to "peek" offset characters ahead.
        can_peek(0) is equivalent to has_next(). The invariant is that if
        can_peek(offset) is true, then peek(offset) returns a valid value. If
        can_peek(offset) is false, then peek(offset) would throw a
        StopIteration exception.
        """
        if offset < 0:
            raise ValueError(f"Invalid negative offset: {offset}")
        return offset <= len(self._buffer) - 1

    def peek(self, offset=0) -> str:
        """
        Returns the character that would be returned by a call to next(),
        without advancing. Raises StopIteration if there is no more character
        to read.
        """
        if offset < 0:
            raise ValueError(f"Invalid negative offset: {offset}")
        if offset > len(self._buffer) - 1:
            raise StopIteration
        return self._buffer[offset].char
