"""
Setuptools command integration for Gauge.

This module provides setuptools command integration, allowing users to run
Gauge tasks through setuptools/distutils commands.

Usage:
    python setup.py gauge
    python setup.py gauge --parallel --nodes=4
    python setup.py gauge_validate
    python setup.py gauge_format
"""

try:
    from setuptools import Command
    SETUPTOOLS_AVAILABLE = True
except ImportError:
    SETUPTOOLS_AVAILABLE = False
    # Fallback class for when setuptools is not available
    class Command:
        pass

from .core import GaugePlugin


class GaugeCommand(Command):
    """Setuptools command to run Gauge specifications."""

    description = "Run Gauge specifications"
    user_options = [
        ('specs-dir=', None, 'Gauge specs directory path'),
        ('tags=', None, 'Filter specs by tags expression'),
        ('parallel', 'p', 'Execute specs in parallel'),
        ('nodes=', 'n', 'Number of parallel execution streams'),
        ('env=', 'e', 'Gauge environment to run against'),
        ('additional-flags=', None, 'Additional gauge flags'),
        ('project-dir=', None, 'Path to gauge project directory'),
        ('gauge-root=', None, 'Path to gauge installation root'),
        ('specs=', None, 'Specific spec files to run (comma-separated)'),
    ]

    boolean_options = ['parallel']

    def initialize_options(self):
        """Initialize command options to None."""
        self.specs_dir = None
        self.tags = None
        self.parallel = False
        self.nodes = None
        self.env = None
        self.additional_flags = None
        self.project_dir = None
        self.gauge_root = None
        self.specs = None

    def finalize_options(self):
        """Finalize and validate command options."""
        if self.nodes is not None:
            try:
                self.nodes = int(self.nodes)
                if self.nodes < 1:
                    raise ValueError("nodes must be at least 1")
            except ValueError as e:
                raise ValueError(f"Invalid nodes value: {e}")

        if self.parallel:
            if self.nodes is None:
                self.nodes = 2  # Default to 2 nodes for parallel execution

    def run(self):
        """Execute the Gauge command."""
        try:
            # Build configuration from options
            config_dict = {}

            if self.specs_dir:
                config_dict["specs_dir"] = self.specs_dir
            if self.tags:
                config_dict["tags"] = self.tags
            if self.parallel:
                config_dict["in_parallel"] = True
            if self.nodes:
                config_dict["nodes"] = self.nodes
            if self.env:
                config_dict["env"] = self.env
            if self.additional_flags:
                config_dict["additional_flags"] = self.additional_flags
            if self.project_dir:
                config_dict["project_dir"] = self.project_dir
            if self.gauge_root:
                config_dict["gauge_root"] = self.gauge_root

            # Create and configure plugin
            plugin = GaugePlugin()
            task = plugin.create_task(config_dict)

            # Parse specific specs if provided
            spec_files = None
            if self.specs:
                spec_files = [spec.strip() for spec in self.specs.split(',')]

            # Run the task
            success = task.run(spec_files)

            if success:
                print("Gauge execution completed successfully")
            else:
                print("Gauge execution failed")
                raise SystemExit(1)

        except Exception as e:
            print(f"Error running Gauge: {e}")
            raise SystemExit(1)


class GaugeValidateCommand(Command):
    """Setuptools command to validate Gauge project."""

    description = "Validate Gauge project"
    user_options = [
        ('specs-dir=', None, 'Gauge specs directory path'),
        ('project-dir=', None, 'Path to gauge project directory'),
        ('gauge-root=', None, 'Path to gauge installation root'),
    ]

    def initialize_options(self):
        """Initialize command options to None."""
        self.specs_dir = None
        self.project_dir = None
        self.gauge_root = None

    def finalize_options(self):
        """Finalize command options."""
        pass

    def run(self):
        """Execute the Gauge validate command."""
        try:
            # Build configuration from options
            config_dict = {}

            if self.specs_dir:
                config_dict["specs_dir"] = self.specs_dir
            if self.project_dir:
                config_dict["project_dir"] = self.project_dir
            if self.gauge_root:
                config_dict["gauge_root"] = self.gauge_root

            # Create and configure plugin
            plugin = GaugePlugin()
            task = plugin.create_task(config_dict)

            # Run validation
            success = task.validate()

            if success:
                print("Gauge project validation completed successfully")
            else:
                print("Gauge project validation failed")
                raise SystemExit(1)

        except Exception as e:
            print(f"Error validating Gauge project: {e}")
            raise SystemExit(1)


class GaugeFormatCommand(Command):
    """Setuptools command to format Gauge specs."""

    description = "Format Gauge specification files"
    user_options = [
        ('specs-dir=', None, 'Gauge specs directory path'),
        ('project-dir=', None, 'Path to gauge project directory'),
        ('gauge-root=', None, 'Path to gauge installation root'),
    ]

    def initialize_options(self):
        """Initialize command options to None."""
        self.specs_dir = None
        self.project_dir = None
        self.gauge_root = None

    def finalize_options(self):
        """Finalize command options."""
        pass

    def run(self):
        """Execute the Gauge format command."""
        try:
            # Build configuration from options
            config_dict = {}

            if self.specs_dir:
                config_dict["specs_dir"] = self.specs_dir
            if self.project_dir:
                config_dict["project_dir"] = self.project_dir
            if self.gauge_root:
                config_dict["gauge_root"] = self.gauge_root

            # Create and configure plugin
            plugin = GaugePlugin()
            task = plugin.create_task(config_dict)

            # Run formatting
            success = task.format_specs()

            if success:
                print("Gauge specs formatting completed successfully")
            else:
                print("Gauge specs formatting failed")
                raise SystemExit(1)

        except Exception as e:
            print(f"Error formatting Gauge specs: {e}")
            raise SystemExit(1)


# Register commands for setuptools entry points
def get_setuptools_commands():
    """Return dictionary of setuptools commands for entry points."""
    if not SETUPTOOLS_AVAILABLE:
        return {}

    return {
        'gauge': GaugeCommand,
        'gauge_validate': GaugeValidateCommand,
        'gauge_format': GaugeFormatCommand,
    }
