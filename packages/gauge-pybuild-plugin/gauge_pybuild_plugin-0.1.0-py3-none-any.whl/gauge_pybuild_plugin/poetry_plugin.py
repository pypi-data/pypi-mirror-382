"""
Poetry plugin integration for Gauge.

This module provides Poetry plugin integration, allowing users to run
Gauge tasks directly through Poetry commands.

Usage:
    poetry gauge run
    poetry gauge validate
    poetry gauge format
    poetry gauge install <plugin>
"""

try:
    from cleo.helpers import argument, option
    from poetry.console.application import Application
    from poetry.console.commands.command import Command as PoetryCommand
    from poetry.plugins.application_plugin import ApplicationPlugin
    POETRY_AVAILABLE = True
except ImportError:
    POETRY_AVAILABLE = False
    # Fallback classes for when Poetry is not available
    class ApplicationPlugin:
        pass
    class PoetryCommand:
        pass

from .core import GaugePlugin


class GaugeRunCommand(PoetryCommand):
    """Command to run Gauge specs through Poetry."""

    name = "gauge run"
    description = "Run Gauge specifications"

    arguments = [
        argument("specs", "Specification files to run", optional=True, multiple=True)
    ]

    options = [
        option("specs-dir", None, "Gauge specs directory path", flag=False),
        option("tags", None, "Filter specs by tags expression", flag=False),
        option("parallel", "p", "Execute specs in parallel"),
        option("nodes", "n", "Number of parallel execution streams", flag=False),
        option("env", "e", "Gauge environment to run against", flag=False),
        option("additional-flags", None, "Additional gauge flags", flag=False),
        option("project-dir", None, "Path to gauge project directory", flag=False),
        option("gauge-root", None, "Path to gauge installation root", flag=False),
    ]

    def handle(self) -> int:
        """Handle the gauge run command."""
        try:
            # Build configuration from options
            config_dict = {}

            if self.option("specs-dir"):
                config_dict["specs_dir"] = self.option("specs-dir")
            if self.option("tags"):
                config_dict["tags"] = self.option("tags")
            if self.option("parallel"):
                config_dict["in_parallel"] = True
            if self.option("nodes"):
                config_dict["nodes"] = int(self.option("nodes"))
            if self.option("env"):
                config_dict["env"] = self.option("env")
            if self.option("additional-flags"):
                config_dict["additional_flags"] = self.option("additional-flags")
            if self.option("project-dir"):
                config_dict["project_dir"] = self.option("project-dir")
            if self.option("gauge-root"):
                config_dict["gauge_root"] = self.option("gauge-root")

            # Create and configure plugin
            plugin = GaugePlugin()
            task = plugin.create_task(config_dict)

            # Get spec files if provided
            specs = self.argument("specs") if self.argument("specs") else None

            # Run the task
            success = task.run(specs)

            if success:
                self.line("<info>Gauge execution completed successfully</info>")
                return 0
            else:
                self.line("<error>Gauge execution failed</error>")
                return 1

        except Exception as e:
            self.line(f"<error>Error running Gauge: {e}</error>")
            return 1


class GaugeValidateCommand(PoetryCommand):
    """Command to validate Gauge project through Poetry."""

    name = "gauge validate"
    description = "Validate Gauge project"

    options = [
        option("specs-dir", None, "Gauge specs directory path", flag=False),
        option("project-dir", None, "Path to gauge project directory", flag=False),
        option("gauge-root", None, "Path to gauge installation root", flag=False),
    ]

    def handle(self) -> int:
        """Handle the gauge validate command."""
        try:
            # Build configuration from options
            config_dict = {}

            if self.option("specs-dir"):
                config_dict["specs_dir"] = self.option("specs-dir")
            if self.option("project-dir"):
                config_dict["project_dir"] = self.option("project-dir")
            if self.option("gauge-root"):
                config_dict["gauge_root"] = self.option("gauge-root")

            # Create and configure plugin
            plugin = GaugePlugin()
            task = plugin.create_task(config_dict)

            # Run validation
            success = task.validate()

            if success:
                self.line("<info>Gauge project validation completed successfully</info>")
                return 0
            else:
                self.line("<error>Gauge project validation failed</error>")
                return 1

        except Exception as e:
            self.line(f"<error>Error validating Gauge project: {e}</error>")
            return 1


class GaugeFormatCommand(PoetryCommand):
    """Command to format Gauge specs through Poetry."""

    name = "gauge format"
    description = "Format Gauge specification files"

    options = [
        option("specs-dir", None, "Gauge specs directory path", flag=False),
        option("project-dir", None, "Path to gauge project directory", flag=False),
        option("gauge-root", None, "Path to gauge installation root", flag=False),
    ]

    def handle(self) -> int:
        """Handle the gauge format command."""
        try:
            # Build configuration from options
            config_dict = {}

            if self.option("specs-dir"):
                config_dict["specs_dir"] = self.option("specs-dir")
            if self.option("project-dir"):
                config_dict["project_dir"] = self.option("project-dir")
            if self.option("gauge-root"):
                config_dict["gauge_root"] = self.option("gauge-root")

            # Create and configure plugin
            plugin = GaugePlugin()
            task = plugin.create_task(config_dict)

            # Run formatting
            success = task.format_specs()

            if success:
                self.line("<info>Gauge specs formatting completed successfully</info>")
                return 0
            else:
                self.line("<error>Gauge specs formatting failed</error>")
                return 1

        except Exception as e:
            self.line(f"<error>Error formatting Gauge specs: {e}</error>")
            return 1


class GaugeInstallCommand(PoetryCommand):
    """Command to install Gauge plugins through Poetry."""

    name = "gauge install"
    description = "Install Gauge plugin"

    arguments = [
        argument("plugin", "Plugin name to install")
    ]

    options = [
        option("version", "v", "Plugin version to install", flag=False),
        option("gauge-root", None, "Path to gauge installation root", flag=False),
    ]

    def handle(self) -> int:
        """Handle the gauge install command."""
        try:
            plugin_name = self.argument("plugin")
            version = self.option("version")

            # Build configuration from options
            config_dict = {}
            if self.option("gauge-root"):
                config_dict["gauge_root"] = self.option("gauge-root")

            # Create and configure plugin
            plugin = GaugePlugin()
            task = plugin.create_task(config_dict)

            # Install the plugin
            success = task.install_plugin(plugin_name, version)

            if success:
                self.line(f"<info>Gauge plugin '{plugin_name}' installed successfully</info>")
                return 0
            else:
                self.line(f"<error>Failed to install Gauge plugin '{plugin_name}'</error>")
                return 1

        except Exception as e:
            self.line(f"<error>Error installing Gauge plugin: {e}</error>")
            return 1


class GaugePoetryPlugin(ApplicationPlugin):
    """Poetry plugin that adds Gauge commands."""

    def activate(self, application: Application) -> None:
        """Activate the plugin by registering Gauge commands."""
        if not POETRY_AVAILABLE:
            return

        application.command_loader.register_factory("gauge run", lambda: GaugeRunCommand())
        application.command_loader.register_factory("gauge validate", lambda: GaugeValidateCommand())
        application.command_loader.register_factory("gauge format", lambda: GaugeFormatCommand())
        application.command_loader.register_factory("gauge install", lambda: GaugeInstallCommand())
