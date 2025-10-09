# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-08

### Added
- Initial release of Gauge Python Build Plugin
- **UV Support** - Lightning-fast Python package manager integration (10-100x faster than pip)
- **Poetry Integration** - Full Poetry plugin with custom commands (`poetry gauge run`)
- **Setuptools Integration** - Custom setuptools commands for traditional Python projects
- **Standalone CLI** - `gauge-py` command-line interface for direct usage
- **Parallel Execution** - Run Gauge specs in parallel with configurable worker nodes
- **Tag-based Filtering** - Execute specific specs using tag expressions
- **Environment Support** - Run against different environments (dev, test, prod, CI)
- **Flexible Configuration** - TOML-based configuration with sensible defaults
- **Project Validation** - Built-in Gauge project validation
- **Spec Formatting** - Automatic specification file formatting
- **Plugin Management** - Install and manage Gauge plugins
- Comprehensive test suite (32 tests with 100% pass rate)
- CI/CD pipeline with GitHub Actions
  - Tests on Python 3.8-3.13
  - Tests on Linux, macOS, Windows
  - Linting with Ruff
  - Type checking with mypy
  - Security scanning with Bandit and Safety
  - Automatic PyPI publishing on release
- Complete documentation with examples
- Branch protection rules
- Dependabot configuration
- Issue and PR templates
- CODEOWNERS file

### Features
- 🚀 Multiple integration options (UV, Poetry, setuptools, standalone CLI)
- ⚡ Fast dependency installation with UV
- 🏷️ Advanced tag filtering for test selection
- 🌍 Environment-specific test execution
- ⚙️ PEP 621 compliant project configuration
- 🔧 Modern tooling (Ruff, mypy, UV)
- 📦 Professional CI/CD pipeline
- 🛡️ Enterprise-grade branch protection

### Documentation
- Comprehensive README with quick start guides
- UV usage guide with examples
- Development guide
- Contributing guidelines
- Apache 2.0 license

### Infrastructure
- GitHub Actions CI/CD pipeline
- Dependabot for automated dependency updates
- Issue templates for bugs and feature requests
- Pull request template
- Code owner assignments
- Branch protection rules

[0.1.0]: https://github.com/lirany1/gauge-pybuild-plugin/releases/tag/v0.1.0
