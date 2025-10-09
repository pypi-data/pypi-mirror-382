"""
Example usage of the Gauge Python Build Plugin.

This script demonstrates how to use the plugin programmatically
and showcases various configuration options.
"""

from gauge_pybuild_plugin import GaugeConfig, GaugePlugin, GaugeTask


def example_basic_usage():
    """Example of basic plugin usage."""
    print("=== Basic Usage ===")

    # Create a simple configuration
    config = GaugeConfig(
        specs_dir="specs",
        env="dev"
    )

    # Create and run a task
    GaugeTask(config)
    print(f"Running gauge with config: {config}")

    # This would actually run gauge if it's installed
    # success = task.run()
    # print(f"Execution successful: {success}")


def example_parallel_execution():
    """Example of parallel execution configuration."""
    print("\n=== Parallel Execution ===")

    config = GaugeConfig(
        specs_dir="specs",
        in_parallel=True,
        nodes=4,
        env="ci",
        tags="smoke",
        additional_flags="--simple-console --verbose"
    )

    GaugeTask(config)
    print(f"Command args: {config.to_command_args()}")
    print(f"Environment: {config.get_environment()}")


def example_plugin_usage():
    """Example using the high-level plugin interface."""
    print("\n=== Plugin Interface ===")

    # Create plugin (would load from pyproject.toml if available)
    plugin = GaugePlugin()

    # Run with configuration override
    plugin.run_specs(
        in_parallel=True,
        nodes=2,
        env="test",
        tags="regression"
    )
    print("Would run specs with parallel execution")

    # Create custom task
    task = plugin.create_task({
        "specs_dir": "integration_specs",
        "env": "staging"
    })
    print(f"Created custom task with config: {task.config}")


def example_multiple_environments():
    """Example showing different environment configurations."""
    print("\n=== Multiple Environments ===")

    # Development environment
    dev_config = GaugeConfig(
        specs_dir="specs",
        env="dev",
        additional_flags="--verbose"
    )

    # CI environment
    ci_config = GaugeConfig(
        specs_dir="specs",
        in_parallel=True,
        nodes=8,
        env="ci",
        additional_flags="--simple-console",
        environment_variables={
            "gauge_reports_dir": "ci_reports",
            "screenshot_on_failure": "true"
        }
    )

    print(f"Dev command: gauge {' '.join(dev_config.to_command_args())}")
    print(f"CI command: gauge {' '.join(ci_config.to_command_args())}")


def example_custom_configuration():
    """Example of advanced configuration options."""
    print("\n=== Custom Configuration ===")

    config = GaugeConfig(
        specs_dir="custom_specs",
        tags="@api & !@slow",
        in_parallel=True,
        nodes=6,
        env="performance",
        additional_flags="--max-retries=3 --timeout=30s",
        gauge_root="/opt/gauge",
        environment_variables={
            "gauge_reports_dir": "performance_reports",
            "logs_directory": "performance_logs",
            "parallel_streams": "6",
            "enable_multithreading": "true"
        }
    )

    print(f"Custom config command args: {config.to_command_args()}")
    print(f"Environment variables: {config.environment_variables}")


def example_spec_filtering():
    """Example of different ways to filter and run specs."""
    print("\n=== Spec Filtering ===")

    # Tag-based filtering
    configs = [
        GaugeConfig(tags="smoke"),
        GaugeConfig(tags="regression & !slow"),
        GaugeConfig(tags="@api | @ui"),
        GaugeConfig(tags="!@wip & !@manual")
    ]

    for i, config in enumerate(configs, 1):
        print(f"Filter {i}: {config.tags}")
        print(f"  Command: gauge {' '.join(config.to_command_args())}")


if __name__ == "__main__":
    """Run all examples."""
    print("Gauge Python Build Plugin Examples")
    print("=" * 50)

    example_basic_usage()
    example_parallel_execution()
    example_plugin_usage()
    example_multiple_environments()
    example_custom_configuration()
    example_spec_filtering()

    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo actually run Gauge, make sure:")
    print("1. Gauge is installed (https://docs.gauge.org/installation.html)")
    print("2. You have a Gauge project with specs/")
    print("3. You have the appropriate language plugin (e.g., python)")
