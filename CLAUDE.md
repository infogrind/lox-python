# Lox Interpreter in Python

This directory implements the Lox Interpreter from Robert Nystrom's book
"Crafting Interpreters". It is a work in progress.

## Guidelines and Tools

- Tests are in the `tests` subdirectory.
- The project relies on the [`uv` tool](https://docs.astral.sh/uv/) to manage
dependencies.
- Always run `uv run pytest` to verify changes.
- To run the linter, run `ruff check .`.
- Always run `ruff  format --config 'lint.select = ["I001", "I002"]'` to format
the code, don't do it yourself.

## Bug Fixing Process

Always work in this order after having identified a bug:

1. Add test case.
2. Verify test case fails.
3. Add fix.
4. Format code.
5. Verify that the test passes.
6. Create a local commit but NEVER push anything yourself.
