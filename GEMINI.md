# Lox Interpreter in Python

This directory implements the Lox Interpreter from Robert Nystrom's book
"Crafting Interpreters". It is a work in progress.

## Guidelines and Tools

- All tests go in the `tests` subdirectory. The `pytest` framework is used
exclusively.
- The project relies on the [`uv` tool](https://docs.astral.sh/uv/) to manage
dependencies.
- The command to run the tests is `uv run pytest`.
- The command to run the linter is `ruff check .`.
- The command to fix formatting is `ruff  format --config 'lint.select =
["I001", "I002"]'`.
- When implementing new language features, don't add new test files by default.
Use the existing test files.
- Always use Python type annotations. If that is not possible for some reason,
state this explicitly and ask for permission to omit them.

## Separate Planning from Implementation

When asked to make a plan, never make any changes to any files yet, just research and then state your plan. Mention explicitly which files you would edit.

## General Development Process

Always use this order, both when adding a feature and when fixing a bug.

1. Add test case. (If needed, add empty function or datatype to make the test compile.)
2. Verify that test case fails.
3. Implement the fix.
4. Format the code.
5. Verify that the test passes.
6. Create a local commit but NEVER push anything yourself.

## Special Guidelines for Implementing Support for New Syntax Elements

Implement the parser test and code first (always respecting the general
development process), then add support to the interpreter. Finally, add a test to test_main_interactive.py to ensure the full diagnostic output is correct.

For example, suppose you are adding support for `if` clauses. You would then do things in this order:

1. Add a definition for the AST element to syntax.py.
2. Update the comment block at the top of syntax.py.
3. Write tests in tests/test_parser.py.
4. Verify that the tests fail.
5. Implement parsing functionality in parser.py.
6. Verify that the tests pass.
7. Write tests in tests/test_interpreter.py.
8. Verify that the interpreter tests fail.
9. Implement interpreter support in interpreter.py.
10. Verify that the tests pass.
11. Add a test (or several tests if needed) to tests/test_main_interactive.py.
12. Verify that the test or tests in tests/test_main_interactive.py pass.
13. Run the formatter to ensure code style is adhered to.
14. Run all tests again, to ensure there are no regressions.
15. Create the local commit.

## Commit Message Guidelines

- Use backticks for code in commit messages

## References

- See <https://craftinginterpreters.com/appendix-i.html> for the Lox Grammar reference

## Git Repo

- The main branch for this project is called `main`.
- When creating commits with multiline messages, write the message to a file
`commit_message.txt`, then commit with `git commit -F commit_message.txt`.
- When staging code changes, and GEMINI.md also has changes, never stage
GEMINI.md. GEMINI.md must always be in separate commits that are only about
Gemini instructions.
- The first line of a commit message should not be longer than 72 characters,
and all the other lines should have a maximum of 100 characters.

# GEMINI.md Memory Updates

Whenever I prefix a prompt with the hash sign `#`, it means I want you to memorize the instruction in GEMINI.md. In that case, please update GEMINI.md accordingly.
