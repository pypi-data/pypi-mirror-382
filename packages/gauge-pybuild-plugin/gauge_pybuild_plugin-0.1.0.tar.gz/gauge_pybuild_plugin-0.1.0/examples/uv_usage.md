# Using Gauge Python Build Plugin with UV

UV is a modern, Rust-based Python package manager that's 10-100x faster than pip. This guide shows how to use the Gauge Python Build Plugin with UV.

## Why UV?

- ⚡ **10-100x faster** than pip/Poetry
- 🦀 **Rust-based** - single binary, no Python required
- 💾 **Efficient** - global package cache
- 🔒 **Reliable** - deterministic dependency resolution
- 🎯 **Simple** - works just like pip but faster

## Installation

### 1. Install UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### 2. Install Gauge Plugin

```bash
# In your Gauge project directory
uv pip install gauge-pybuild-plugin

# Or add to requirements
uv add gauge-pybuild-plugin
```

## Basic Usage

### Run Gauge Specs

```bash
# Run all specs
uv run gauge-py run

# Run with parallel execution
uv run gauge-py run --parallel --nodes=4

# Run specific specs
uv run gauge-py run specs/login.spec

# Run with tags
uv run gauge-py run --tags="smoke"
```

### Validate and Format

```bash
# Validate Gauge project
uv run gauge-py validate

# Format specifications
uv run gauge-py format
```

### Manage Plugins

```bash
# Install Gauge plugins
uv run gauge-py install python
uv run gauge-py install html-report
```

## Advanced Examples

### Environment-Specific Runs

```bash
# Development environment
uv run gauge-py run --env=dev

# CI environment with parallel execution
uv run gauge-py run --env=ci --parallel --nodes=8

# Production smoke tests
uv run gauge-py run --env=prod --tags="smoke"
```

### Tag Combinations

```bash
# Run smoke tests only
uv run gauge-py run --tags="smoke"

# Run regression, exclude slow tests
uv run gauge-py run --tags="regression & !slow"

# API or UI tests
uv run gauge-py run --tags="@api | @ui"

# Everything except WIP and manual
uv run gauge-py run --tags="!@wip & !@manual"
```

### Custom Flags

```bash
# Verbose output
uv run gauge-py --verbose run

# Simple console output
uv run gauge-py run --additional-flags="--simple-console"

# Multiple flags
uv run gauge-py run --additional-flags="--simple-console --verbose"
```

## Project Setup with UV

### Create pyproject.toml

```toml
[project]
name = "my-gauge-tests"
version = "0.1.0"
requires-python = ">=3.8"
dependencies = [
    "getgauge>=0.3.7",
    "gauge-pybuild-plugin>=0.1.0",
]

[tool.gauge]
specs_dir = "specs"
in_parallel = true
nodes = 4
env = "default"

[tool.gauge.environment_variables]
gauge_reports_dir = "reports"
logs_directory = "logs"
```

### Initialize and Run

```bash
# Install dependencies
uv pip install -r pyproject.toml

# Or use uv sync (recommended)
uv sync

# Run tests
uv run gauge-py run
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Gauge Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install UV
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install Gauge
        run: |
          curl -SsL https://downloads.gauge.org/stable | sh
          gauge install python
      
      - name: Install dependencies
        run: uv pip install -e .
      
      - name: Run tests
        run: uv run gauge-py run --parallel --nodes=4 --env=ci
```

### GitLab CI Example

```yaml
test:
  image: python:3.12
  before_script:
    - curl -LsSf https://astral.sh/uv/install.sh | sh
    - curl -SsL https://downloads.gauge.org/stable | sh
    - gauge install python
    - uv pip install -e .
  script:
    - uv run gauge-py run --parallel --nodes=4
```

## Performance Comparison

| Operation | pip | Poetry | UV |
|-----------|-----|--------|-----|
| Install from cache | 5s | 8s | 0.1s |
| Fresh install | 30s | 25s | 2s |
| Lock resolution | 10s | 15s | 0.5s |

## Tips & Best Practices

### 1. Use UV for Development

```bash
# Install in editable mode
uv pip install -e ".[dev]"

# Run tests during development
uv run pytest
```

### 2. Cache Dependencies

UV automatically caches packages globally, making repeated installs instant.

### 3. Virtual Environment Management

```bash
# UV creates virtual environments automatically
uv venv

# Activate manually if needed
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 4. Lock Dependencies

```bash
# Generate lock file
uv pip compile pyproject.toml -o requirements.txt

# Install from lock file
uv pip sync requirements.txt
```

## Migrating from Poetry

If you're currently using Poetry:

```bash
# 1. Keep your pyproject.toml (UV reads it)
# 2. Just use UV commands instead

# Before (Poetry)
poetry install
poetry run gauge-py run

# After (UV)
uv pip install -e .
uv run gauge-py run
```

You can keep both! UV is compatible with Poetry's pyproject.toml format.

## Troubleshooting

### UV not found after installation

```bash
# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Reload shell
source ~/.bashrc  # or source ~/.zshrc
```

### Command not found: gauge-py

```bash
# Make sure the package is installed
uv pip list | grep gauge-pybuild-plugin

# Reinstall if needed
uv pip install --force-reinstall gauge-pybuild-plugin
```

### Virtual environment issues

```bash
# Create a new virtual environment
uv venv --python 3.12

# Install in the venv
uv pip install gauge-pybuild-plugin
```

## Resources

- [UV Documentation](https://github.com/astral-sh/uv)
- [Gauge Documentation](https://docs.gauge.org/)
- [Plugin Repository](https://github.com/lirany1/gauge-pybuild-plugin)
