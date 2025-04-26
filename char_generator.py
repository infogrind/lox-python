from dataclasses import dataclass
from typing import Iterator


class Diagnostics:
    """
    Represents the information to diagnose problems related to a specific read
    character: At which line and column it was found, and a string with the
    actual line. It also offers functionality to print a human-readable string
    indicating at which place exactly an error occurred.
    """

    def __init__(self, line_no, col_no, line):
        self._line_no: int = line_no
        self._col_no: int = col_no
        self._line: str = line

    def diagnostic_string(self) -> str:
        if self._line is None:
            raise RuntimeError("No diagnostics for uninitialized state.")

        line_prefix = f"{self._line_no:>5}: "
        output = [line_prefix + self._line]
        arrow_indent = " " * len(line_prefix) + " " * (self._col_no - 1)
        output.append(arrow_indent + "^")
        output.append(arrow_indent + "┗--- here")
        return "\n".join(output)

    def next_col(self) -> "Diagnostics":
        """
        Returns a diagnostics object corresponding to one column advanced
        from the current one. This is to have an object that points to the
        column _after_ the last character, in case there were any missing
        characters such as missing closing quote or closing parenthesis.
        """
        return Diagnostics(self._line_no, self._col_no + 1, self._line)


@dataclass
class ReadCharState:
    """
    Represents a read character with its diagnostic state. This is stored in
    the char reader's buffer.
    """

    char: str
    diags: Diagnostics


def char_generator(line_iter: Iterator[str]) -> Iterator[ReadCharState]:
    """
    Returns a generator that produces successive characters from an iterator
    of lines. The lines may or may not contain trailing newlines; if they do,
    the newlines are returned like any other character.

    The returned characters are encapsulated together with diagnostic state
    in a _ReadCharState object.
    """
    for i, line in enumerate(line_iter):
        for j, char in enumerate(line):
            yield ReadCharState(char, Diagnostics(i + 1, j + 1, line.rstrip()))
