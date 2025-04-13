# lox-python

A Python version of the Lox interpreter from [Crafting
Interpreters](https://www.goodreads.com/book/show/58661468-crafting-interpreters)
by Bob Nystrom.

This is just a personal project to get familiar wity Python and to learn new
interpreter techniques.

## Usage

The recommended way to manage dependencies and run this is using [`uv`](https://github.com/astral-sh/uv).

To run the program with a manual REPL loop:

```shell
uv run --script main.py
```

To run with some testdata file:

```shell
uv run --script main.py testdata/tokens.txt
```

* Unit tests: `uv run pytest`
* Unit tests with program output and summary: `uv run pytest -rA -s`
