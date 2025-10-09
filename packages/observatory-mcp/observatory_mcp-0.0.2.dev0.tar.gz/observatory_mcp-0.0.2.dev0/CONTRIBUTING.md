# Contributing to Observatory Python SDK

Thank you for your interest in contributing! This document provides guidelines for contributing to the Observatory Python SDK.

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Git
- pip

### Development Setup

1. **Fork and clone the repository**

```bash
git clone https://github.com/yourusername/observatory.git
cd observatory/sdk/python-sdk
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies**

```bash
pip install -e ".[dev]"
```

4. **Run tests to verify setup**

```bash
pytest
```

## Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation changes
- `refactor/` - Code refactoring
- `test/` - Test additions or fixes

### 2. Make Your Changes

- Write clear, concise code
- Follow existing code style
- Add tests for new functionality
- Update documentation as needed

### 3. Code Quality

Run code quality checks before committing:

```bash
# Format code
black observatory_mcp/

# Lint code
ruff check observatory_mcp/

# Type check
mypy observatory_mcp/

# Run tests
pytest --cov=observatory_mcp
```

### 4. Commit Your Changes

Write clear commit messages:

```bash
git add .
git commit -m "feat: add custom sampling strategy support"
```

Commit message format:
- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test changes
- `refactor:` - Code refactoring
- `chore:` - Maintenance tasks

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub.

## Code Style

### Python Style Guide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://black.readthedocs.io/) for formatting (100 char line length)
- Use type hints for all function signatures
- Write docstrings for all public functions and classes

### Docstring Format

```python
def function_name(param1: str, param2: int) -> bool:
    """Brief description of function.

    More detailed description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When and why this is raised
    """
    pass
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Aim for >90% code coverage

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=observatory_mcp --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::test_sampling_config_defaults
```

## Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update CHANGELOG.md

### Building Documentation

Documentation is in Markdown format:
- `README.md` - Main documentation
- `docs/quickstart.md` - Quick start guide
- `docs/api_reference.md` - API reference
- `examples/` - Code examples

## Pull Request Process

1. **Ensure CI passes**
   - All tests pass
   - Code is formatted with Black
   - No linting errors
   - Type checking passes

2. **Update documentation**
   - README if user-facing changes
   - CHANGELOG.md with your changes
   - Docstrings for new code

3. **Write a clear PR description**
   - What changes were made
   - Why the changes were needed
   - How to test the changes

4. **Request review**
   - Tag maintainers for review
   - Address feedback promptly

5. **Squash commits if needed**
   - Keep git history clean
   - One logical change per commit

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `__init__.py`
2. Update CHANGELOG.md
3. Create git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. GitHub Actions will automatically publish to PyPI

## Questions?

- Open an issue for bugs or feature requests
- Join our Discord for discussions
- Email: dev@observatory.dev

## Code of Conduct

Be respectful, inclusive, and constructive. We're all here to build great software together.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
