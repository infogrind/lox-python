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

- Unit tests: `uv run pytest`
- Unit tests with program output and summary: `uv run pytest -rA -s`
- Monitor changes and run tests: `fd '\.py$' | entr -c -s 'uv run pytest'` (needs `entr`).

## Test Coverage

To get coverage data, run

```shell
uv run coverage run -m pytest
```

To generate the coverage report, run

```shell
uv run coverage html
```

To see a summary report in the terminal, run

```shell
uv run coverage report
```
