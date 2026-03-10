# Contributing to WOOFi Python SDK

This project uses `hatchling` as the build backend.

## Setup

Clone the repository and install the package in editable mode along with development dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Testing & Linting

We use `pytest` for testing, `ruff` for linting, and `mypy` for type checking.

```bash
# Run tests
pytest

# Run linter
ruff check src tests

# Run type checker
mypy src
```

## Build

To build the wheel and sdist packages:

```bash
pip install build
python -m build
```
