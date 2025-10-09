"""
Test configuration and utilities for Gauge Python Build Plugin tests.
"""

import shutil
import tempfile
from pathlib import Path
from typing import Generator

import pytest


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path)


@pytest.fixture
def mock_gauge_project(temp_dir: Path) -> Path:
    """Create a mock Gauge project structure."""
    # Create specs directory
    specs_dir = temp_dir / "specs"
    specs_dir.mkdir()

    # Create a sample spec file
    spec_content = """
# Sample Specification

This is a sample specification for testing.

## Scenario 1
* Step one
* Step two

## Scenario 2
* Step three
* Step four
"""
    (specs_dir / "sample.spec").write_text(spec_content)

    # Create manifest.json
    manifest_content = """{
  "Language": "python",
  "Plugins": ["html-report", "python"]
}"""
    (temp_dir / "manifest.json").write_text(manifest_content)

    # Create env directory
    env_dir = temp_dir / "env"
    env_dir.mkdir()
    (env_dir / "default.properties").write_text("# Default environment")

    return temp_dir


@pytest.fixture
def sample_config_file(temp_dir: Path) -> Path:
    """Create a sample configuration file."""
    config_content = """
[tool.gauge]
specs_dir = "specs"
in_parallel = false
nodes = 1
env = "default"
additional_flags = "--verbose"

[tool.gauge.environment_variables]
gauge_reports_dir = "reports"
"""
    config_file = temp_dir / "pyproject.toml"
    config_file.write_text(config_content)
    return config_file
