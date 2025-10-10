# YAML Lex Formatter

yaml-lex is a Python tool for reformatting YAML files with specific wrapping rules.

It is designed to make YAML files more readable and maintainable, particularly for content-heavy nodes like content, caption, and title.

## Features

✅ Wraps long strings at a configurable line width
✅ Preserves blank lines and paragraph breaks
✅ Converts long text into block scalars (|-) for YAML readability
✅ Special rules for common keys:
    - `content` → always block scalar unless it contains a Markdown table
    - `caption` / `title` → flattened into single line, then wrapped if too long
    - Other long strings → wrapped into block scalars
✅ Detects and preserves Markdown tables (avoids breaking table formatting)
✅ Works on a single file or recursively on a folder of YAML files
✅ In-place editing or output to a new file

## Notes

- Rich logging using rich.
- Fully compatible with doctest-style examples for testing.
- Supports CI/CD workflows with testing, linting, pre-commit hooks, and docs building.
