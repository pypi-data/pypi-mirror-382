"""
Gauge Python Build Plugin

A comprehensive build plugin for Gauge testing framework that integrates with
Poetry, setuptools, and provides standalone CLI functionality.

Similar to the Gauge Gradle plugin, this provides:
- Execute Gauge specs with various configurations
- Parallel execution support
- Environment-specific runs
- Tag-based filtering
- Validation of Gauge projects
- Custom task creation
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__license__ = "Apache-2.0"

from .core import GaugeConfig, GaugePlugin, GaugeTask

__all__ = ["GaugeConfig", "GaugeTask", "GaugePlugin"]
