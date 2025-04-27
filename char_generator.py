from dataclasses import dataclass
from typing import Iterator
from diagnostics import Diagnostics, Pos


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
            yield ReadCharState(char, Diagnostics(Pos(i + 1, j + 1), line.rstrip()))
