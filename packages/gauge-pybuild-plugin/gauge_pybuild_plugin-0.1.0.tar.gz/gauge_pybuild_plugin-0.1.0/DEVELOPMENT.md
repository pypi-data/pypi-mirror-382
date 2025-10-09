# Gauge Python Build Plugin Development

## Development Setup

```bash
# Clone the repository
git clone https://github.com/lirany1/gauge-pybuild-plugin.git
cd gauge-pybuild-plugin

# Install Poetry if not already installed
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Install pre-commit hooks
poetry run pre-commit install
```

## Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=gauge_pybuild_plugin --cov-report=html

# Run specific test file
poetry run pytest tests/test_core.py

# Run with verbose output
poetry run pytest -v
```

## Code Quality

```bash
# Format code
poetry run black src/ tests/

# Sort imports
poetry run isort src/ tests/

# Type checking
poetry run mypy src/

# Linting
poetry run flake8 src/ tests/
```

## Building and Publishing

```bash
# Build the package
poetry build

# Check the built package
poetry run twine check dist/*

# Publish to TestPyPI
poetry config repositories.testpypi https://test.pypi.org/legacy/
poetry publish -r testpypi

# Publish to PyPI
poetry publish
```

## Testing with Real Gauge Projects

```bash
# Create a test Gauge project
gauge init python

# Install the plugin from local source
pip install -e /path/to/gauge-pybuild-plugin

# Test the CLI
gauge-py run

# Test Poetry integration (in the gauge project)
poetry add /path/to/gauge-pybuild-plugin
poetry gauge run
```

## Project Structure

```
gauge-pybuild-plugin/
├── src/
│   └── gauge_pybuild_plugin/
│       ├── __init__.py           # Main package exports
│       ├── core.py               # Core functionality
│       ├── cli.py                # Command-line interface
│       ├── poetry_plugin.py      # Poetry plugin integration
│       └── setuptools_command.py # Setuptools command integration
├── tests/
│   ├── conftest.py              # Test configuration
│   ├── test_core.py             # Core functionality tests
│   └── test_cli.py              # CLI tests
├── examples/
│   └── example_usage.py         # Usage examples
├── pyproject.toml               # Project configuration
├── README.md                    # Documentation
└── LICENSE                      # Apache 2.0 license
```

## Release Process

1. Update version in `pyproject.toml` and `__init__.py`
2. Update `CHANGELOG.md` with release notes
3. Create a git tag: `git tag v0.1.0`
4. Push tag: `git push origin v0.1.0`
5. Build and publish: `poetry publish --build`
6. Create GitHub release with release notes

## Architecture Notes

The plugin is designed with three integration points:

1. **Poetry Plugin**: Registers commands like `poetry gauge run`
2. **Setuptools Commands**: Provides `python setup.py gauge`
3. **Standalone CLI**: Offers `gauge-py run` for direct usage

The core functionality is shared across all three interfaces through the `GaugePlugin`, `GaugeTask`, and `GaugeConfig` classes.

## Configuration Loading Priority

1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration file (`pyproject.toml` or `gauge.toml`)
4. Default values (lowest priority)

## Error Handling

The plugin follows these error handling principles:

- Return `False` from task methods for recoverable failures
- Raise exceptions for configuration or setup errors
- Use appropriate exit codes in CLI (0 for success, 1 for failure)
- Provide clear error messages with actionable suggestions