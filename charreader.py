from dataclasses import dataclass, replace
from typing import Iterator


@dataclass
class _DiagnosticState:
    """
    Represents the information to diagnose problems related to a specific read
    character: At which line and column it was found, and a string with the
    actual line.

    The invariant is that this is in sync with the head char, except in these
    cases:
    - If the end of input has been reached, head_char will be None, but the
      diagnostic state will still be that of the previous character.
    - If there was never any input (we started out with an empty input), then
      the diagnostic state is None.
    """

    col_no: int  # The column at which the character was located.
    line_no: int  # Dito for the line.
    line: str | None  # The actual line of input.


class CharReader:
    """
    A reader to read characters from successive lines. Offers a peek()
    functionality for lookahead.
    """

    def __init__(self, line_iter: Iterator[str]):
        self._line_iter = line_iter

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
        self._advance_char()

    def _advance_line(self):
        """
        Loads the next line from the input iterator into head_line and resets
        the char_iter. If the input iterator has no more elements, head_line is
        set to None.
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
                self._last_processed_state.line_no = (
                    self._last_processed_state.line_no + 1
                )
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

    def _advance_char(self):
        """
        Loads the next character from the current line into head_char, to make
        it accessible by peek(). If there are no more characters, head_char is
        set to none.
        """
        if self._head_line is None:
            # No more lines in line iterator, therefore also no more characters.
            self._head_char = None
            return
        try:
            self._head_char = next(self._char_iter)
            self._last_processed_state.col_no = self._last_processed_state.col_no + 1

            # Just to placate the linter and fail explicitly. But since _head_line is not None, it
            # means that _last_processed_line has been set.
            if self._last_processed_state.line is None:
                raise RuntimeError(
                    "Internal error: expected _last_processed_line to not be None."
                )

            # Update read state
            self._head_state = replace(self._last_processed_state)
        except StopIteration:
            # First see if there is another line to read.
            self._advance_line()
            if self._head_line is None:
                # We have reached the end of characters and lines.
                self._head_char = None

                # We lead _head_state untouched because we want to keep the
                # diagnostic information of the previously read character. This
                # allows us to show things like "unexpected end of input at
                # ...".
            else:
                try:
                    self._head_char = next(self._char_iter)
                    self._last_processed_state.col_no = (
                        self._last_processed_state.col_no + 1
                    )

                    # Placate the linter
                    if self._last_processed_state.line is None:
                        raise RuntimeError(
                            "Internal error: expected _last_processed_line to not be None."
                        )

                    self._head_state = replace(self._last_processed_state)

                except StopIteration:
                    # We must have read an empty line. That is a bug, because load_line should skip
                    # empty lines.
                    raise RuntimeError("Illegal state detected, probably a bug.")

    def line_no(self) -> int:
        """
        Returns the number of the last processed line.
        """
        return 0 if self._head_state is None else self._head_state.line_no

    def char_no(self) -> int:
        """
        Returns the number of the last processed character in the current line,
        or 0 if no character has been processed (e.g. if the current line is an
        empty line).

        "Processed" means it has actually been read from the input and is
        available to next() or peek().
        """
        return 0 if self._head_state is None else self._head_state.col_no

    def diagnostic_string(self) -> str:
        """
        Returns a string that shows the last processed line and visually
        depicts the last processed position. Useful for error messages.
        """
        if self._head_state.line is None:
            return "  (can't determine position, maybe there was no input at all)"

        # The entire diagnostic message is indented by two spaces.
        line_prefix = f"{self._head_state.line_no:>5}: "
        output = [line_prefix + self._head_state.line]
        arrow_indent = " " * len(line_prefix) + " " * (self._head_state.col_no - 1)
        output.append(arrow_indent + "^")
        output.append(arrow_indent + "┗--- here")
        return "\n".join(output)

    def next(self) -> str:
        """
        Returns the next character and advances to the next character.
        Raises StopIteration if there are no more characters.
        """
        if self._head_char is None:
            raise StopIteration

        result = self._head_char
        self._advance_char()
        return result

    def has_next(self) -> bool:
        """
        Returns True if there is still a character to read, false otherwise.
        """
        return self._head_char is not None

    def peek(self) -> str:
        """
        Returns the character that would be returned by a call to next(),
        without advancing. Raises StopIteration if there is no more character
        to read.
        """
        if self._head_char is None:
            raise StopIteration
        return self._head_char
