"""
Command-line interface for Gauge Python Build Plugin.

This module provides a standalone CLI that can be used independently
of Poetry or setuptools, similar to how the Gradle plugin can be invoked
directly through gradle commands.

Usage:
    gauge-py run [OPTIONS] [SPECS]
    gauge-py validate [OPTIONS]
    gauge-py format [OPTIONS]
    gauge-py install [OPTIONS] PLUGIN
    gauge-py config [OPTIONS]
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

import click
import toml

from .core import GaugePlugin


@click.group()
@click.option('--config', '-c', type=click.Path(exists=True),
              help='Path to configuration file (pyproject.toml or gauge.toml)')
@click.option('--project-dir', type=click.Path(exists=True),
              help='Path to gauge project directory')
@click.option('--gauge-root', type=click.Path(exists=True),
              help='Path to gauge installation root')
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def cli(ctx, config, project_dir, gauge_root, verbose):
    """Gauge Python Build Plugin - Execute Gauge tests with Python build tools."""
    ctx.ensure_object(dict)

    # Store global options
    ctx.obj['config_file'] = config
    ctx.obj['project_dir'] = project_dir
    ctx.obj['gauge_root'] = gauge_root
    ctx.obj['verbose'] = verbose

    # Change to project directory if specified
    if project_dir:
        os.chdir(project_dir)


def load_config_from_file(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from a TOML file."""
    config_data = {}

    # Try to find configuration file
    if config_file:
        config_path = Path(config_file)
    else:
        # Look for pyproject.toml or gauge.toml in current directory
        config_path = Path('pyproject.toml')
        if not config_path.exists():
            config_path = Path('gauge.toml')
        if not config_path.exists():
            return config_data

    if config_path.exists():
        try:
            with open(config_path) as f:
                data = toml.load(f)

            # Extract gauge configuration
            if 'tool' in data and 'gauge' in data['tool']:
                config_data = data['tool']['gauge']
            elif 'gauge' in data:
                config_data = data['gauge']

        except Exception as e:
            click.echo(f"Warning: Failed to load config from {config_path}: {e}", err=True)

    return config_data


def create_gauge_plugin(ctx) -> GaugePlugin:
    """Create a GaugePlugin instance with configuration from context."""
    config_file = ctx.obj.get('config_file')
    return GaugePlugin(config_file)


def build_config_dict(ctx, **kwargs) -> Dict[str, Any]:
    """Build configuration dictionary from context and keyword arguments."""
    config_dict = {}

    # Add global options
    if ctx.obj.get('project_dir'):
        config_dict['project_dir'] = ctx.obj['project_dir']
    if ctx.obj.get('gauge_root'):
        config_dict['gauge_root'] = ctx.obj['gauge_root']

    # Add command-specific options
    for key, value in kwargs.items():
        if value is not None:
            # Convert CLI option names to config names
            if key == 'specs_dir':
                config_dict['specs_dir'] = value
            elif key == 'in_parallel':
                config_dict['in_parallel'] = value
            else:
                config_dict[key] = value

    return config_dict


@cli.command()
@click.argument('specs', nargs=-1)
@click.option('--specs-dir', default='specs', help='Gauge specs directory path')
@click.option('--tags', help='Filter specs by tags expression')
@click.option('--parallel', '-p', is_flag=True, help='Execute specs in parallel')
@click.option('--nodes', '-n', type=int, default=1, help='Number of parallel execution streams')
@click.option('--env', '-e', help='Gauge environment to run against')
@click.option('--additional-flags', help='Additional gauge flags (space-separated)')
@click.pass_context
def run(ctx, specs, specs_dir, tags, parallel, nodes, env, additional_flags):
    """Run Gauge specifications."""
    try:
        # Build configuration
        config_dict = build_config_dict(
            ctx,
            specs_dir=specs_dir,
            tags=tags,
            in_parallel=parallel,
            nodes=nodes,
            env=env,
            additional_flags=additional_flags
        )

        # Create plugin and task
        plugin = create_gauge_plugin(ctx)
        task = plugin.create_task(config_dict)

        # Convert specs tuple to list if provided
        spec_list = list(specs) if specs else None

        if ctx.obj.get('verbose'):
            click.echo(f"Running Gauge with configuration: {config_dict}")
            if spec_list:
                click.echo(f"Specific specs: {spec_list}")

        # Run the task
        success = task.run(spec_list)

        if success:
            click.echo("✅ Gauge execution completed successfully", color=True)
        else:
            click.echo("❌ Gauge execution failed", err=True, color=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error running Gauge: {e}", err=True, color=True)
        sys.exit(1)


@cli.command()
@click.option('--specs-dir', default='specs', help='Gauge specs directory path')
@click.pass_context
def validate(ctx, specs_dir):
    """Validate Gauge project."""
    try:
        # Build configuration
        config_dict = build_config_dict(ctx, specs_dir=specs_dir)

        # Create plugin and task
        plugin = create_gauge_plugin(ctx)
        task = plugin.create_task(config_dict)

        if ctx.obj.get('verbose'):
            click.echo(f"Validating Gauge project with configuration: {config_dict}")

        # Run validation
        success = task.validate()

        if success:
            click.echo("✅ Gauge project validation completed successfully", color=True)
        else:
            click.echo("❌ Gauge project validation failed", err=True, color=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error validating Gauge project: {e}", err=True, color=True)
        sys.exit(1)


@cli.command()
@click.option('--specs-dir', default='specs', help='Gauge specs directory path')
@click.pass_context
def format(ctx, specs_dir):
    """Format Gauge specification files."""
    try:
        # Build configuration
        config_dict = build_config_dict(ctx, specs_dir=specs_dir)

        # Create plugin and task
        plugin = create_gauge_plugin(ctx)
        task = plugin.create_task(config_dict)

        if ctx.obj.get('verbose'):
            click.echo(f"Formatting Gauge specs with configuration: {config_dict}")

        # Run formatting
        success = task.format_specs()

        if success:
            click.echo("✅ Gauge specs formatting completed successfully", color=True)
        else:
            click.echo("❌ Gauge specs formatting failed", err=True, color=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error formatting Gauge specs: {e}", err=True, color=True)
        sys.exit(1)


@cli.command()
@click.argument('plugin_name')
@click.option('--version', '-v', help='Plugin version to install')
@click.pass_context
def install(ctx, plugin_name, version):
    """Install Gauge plugin."""
    try:
        # Build configuration
        config_dict = build_config_dict(ctx)

        # Create plugin and task
        plugin = create_gauge_plugin(ctx)
        task = plugin.create_task(config_dict)

        if ctx.obj.get('verbose'):
            click.echo(f"Installing Gauge plugin '{plugin_name}'" +
                      (f" version {version}" if version else ""))

        # Install the plugin
        success = task.install_plugin(plugin_name, version)

        if success:
            click.echo(f"✅ Gauge plugin '{plugin_name}' installed successfully", color=True)
        else:
            click.echo(f"❌ Failed to install Gauge plugin '{plugin_name}'", err=True, color=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error installing Gauge plugin: {e}", err=True, color=True)
        sys.exit(1)


@cli.command()
@click.option('--show', is_flag=True, help='Show current configuration')
@click.option('--init', is_flag=True, help='Initialize gauge configuration file')
@click.pass_context
def config(ctx, show, init):
    """Manage Gauge configuration."""
    try:
        if init:
            # Create a sample configuration file
            config_content = """
[tool.gauge]
specs_dir = "specs"
in_parallel = false
nodes = 1
env = "default"
additional_flags = ""
environment_variables = {}

# Example for different environments
# [tool.gauge.environments.dev]
# env = "dev"
# additional_flags = "--verbose"
#
# [tool.gauge.environments.ci]
# env = "ci"
# in_parallel = true
# nodes = 4
# additional_flags = "--simple-console"
"""

            config_file = Path('pyproject.toml')
            if config_file.exists():
                click.echo("⚠️  pyproject.toml already exists. Please add the gauge configuration manually.")
                click.echo("Sample configuration:")
                click.echo(config_content)
            else:
                with open(config_file, 'w') as f:
                    build_system = (
                        '[build-system]\n'
                        'requires = ["poetry-core"]\n'
                        'build-backend = "poetry.core.masonry.api"\n'
                    )
                    f.write(f"{build_system}{config_content}")
                click.echo(f"✅ Initialized gauge configuration in {config_file}")

        elif show:
            # Show current configuration
            config_data = load_config_from_file(ctx.obj.get('config_file'))
            if config_data:
                click.echo("Current Gauge configuration:")
                for key, value in config_data.items():
                    click.echo(f"  {key}: {value}")
            else:
                click.echo("No Gauge configuration found.")
                click.echo("Use 'gauge-py config --init' to create a configuration file.")

        else:
            click.echo("Use --show to display current configuration or --init to create a new one.")

    except Exception as e:
        click.echo(f"❌ Error managing configuration: {e}", err=True, color=True)
        sys.exit(1)


def main():
    """Entry point for the gauge-py CLI."""
    cli()


if __name__ == '__main__':
    main()
