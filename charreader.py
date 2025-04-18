from collections import deque
from dataclasses import dataclass, replace
from typing import Deque
from typing import Iterator


@dataclass
class _DiagnosticState:
    """
    Represents the information to diagnose problems related to a specific read
    character: At which line and column it was found, and a string with the
    actual line. It also offers functionality to print a human-readable string
    indicating at which place exactly an error occurred.
    """

    col_no: int  # The column at which the character was located.
    line_no: int  # Dito for the line.
    line: str | None  # The actual line of input.

    def update_line(self, line: str):
        """
        Update the state for a newly read line.
        """
        # We don't keep any trailing newline.
        self.line = line.rstrip()
        self.line_no = self.line_no + 1
        self.col_no = 0

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
    functionality for lookahead, with a configurable buffer length, depending
    on how much lookahead is needed.
    """

    def __init__(self, line_iter: Iterator[str], bufsize: int = 1):
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
        if bufsize < 1:
            # In theory we could also support an unbuffered version, but that
            # is currently not implemented.
            raise ValueError("Buffer size must be positive, to support peeking.")

        ########################################################################
        # Class state and invariants
        ########################################################################

        # Stores the provided iterator, used to fetch new lines from the input.
        self._line_iter: Iterator[str] = line_iter

        # The provided buffer size, immutable.
        self._bufsize = bufsize

        # The buffer itself, implemented as a deque but a simple queue would be
        # enough.
        self._buffer: Deque[_ReadCharState] = deque()

        # This stores the diagnostic state of the latest character successfully
        # read from the input. We keep this explicitly to support the case
        # where the end of the input has been reached, the buffer has been
        # emptied, but we still need this info. This is normally for the error
        # "unexpected end of input: …".
        #
        # If this is None, it means we never read any input, i.e., the given
        # input was empty.
        self._last_processed_state: _DiagnosticState | None = None

        # Initialize the state: load the first line and replenish the buffer.
        self._advance_line()
        self._refill_buffer()

    def _advance_line(self):
        """
        Loads the next non-empty line from the input iterator and resets
        the _char_iter to consume it. After this is called, one of two
        situations arise:
        - char_iter is None, which means the end of the input has been reached,
          or
        - char_iter is not None, in which case we can continue to read
          characters.
        """
        while True:
            try:
                line = next(self._line_iter)

                # Update the diagnostic information.
                if not self._last_processed_state:
                    self._last_processed_state = _DiagnosticState(0, 0, "")
                self._last_processed_state.update_line(line)

                if not line:
                    # Skip over empty lines.
                    continue

                # Reset the iterator that iterates through individual characters.
                self._char_iter = iter(line)
                break

            except StopIteration:
                # End of lines reached
                self._char_iter = None
                return

    def _refill_buffer(self) -> None:
        """
        Loads characters from the input until the buffer is again at _bufsize
        or until the end of the input has been reached.
        """
        while len(self._buffer) < self._bufsize:
            if not self._char_iter:
                # Already at end of input.
                return
            try:
                char = next(self._char_iter)
            except StopIteration:
                # End of current line, need to advance.
                self._advance_line()

                # Continue with the next character.
                continue

            # At this point, we've successfully read the next character.

            # The state should always be set when a character could successfully be read.
            assert self._last_processed_state, "State unexpectedly missing."

            # We've successfully read a character from the current line, so we can update the state.
            self._last_processed_state.increase_col()
            self._buffer.append(
                _ReadCharState(char, replace(self._last_processed_state))
            )

    def line_no(self) -> int:
        """
        Returns the number of the last processed line.
        """
        if self._buffer:
            return self._buffer[0].diags.line_no
        elif self._last_processed_state:
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
        elif self._last_processed_state:
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
        elif self._last_processed_state:
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
