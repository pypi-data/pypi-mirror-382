"""
Tests for the core Gauge plugin functionality.
"""

from unittest.mock import patch

import pytest

from gauge_pybuild_plugin.core import GaugeConfig, GaugePlugin, GaugeTask


class TestGaugeConfig:
    """Test the GaugeConfig class."""

    def test_default_config(self):
        """Test default configuration values."""
        config = GaugeConfig()
        assert config.specs_dir == "specs"
        assert config.tags is None
        assert config.in_parallel is False
        assert config.nodes == 1
        assert config.env is None
        assert config.additional_flags is None
        assert config.project_dir is None
        assert config.gauge_root is None
        assert config.environment_variables == {}

    def test_custom_config(self):
        """Test custom configuration values."""
        config = GaugeConfig(
            specs_dir="custom_specs",
            tags="smoke",
            in_parallel=True,
            nodes=4,
            env="dev",
            additional_flags="--verbose",
            gauge_root="/opt/gauge"
        )
        assert config.specs_dir == "custom_specs"
        assert config.tags == "smoke"
        assert config.in_parallel is True
        assert config.nodes == 4
        assert config.env == "dev"
        assert config.additional_flags == "--verbose"
        assert config.gauge_root == "/opt/gauge"

    def test_nodes_validation(self):
        """Test nodes validation."""
        with pytest.raises(ValueError, match="nodes must be at least 1"):
            GaugeConfig(nodes=0)

    def test_to_command_args(self):
        """Test command arguments generation."""
        config = GaugeConfig(
            specs_dir="specs",
            tags="smoke",
            in_parallel=True,
            nodes=4,
            env="dev",
            additional_flags="--verbose --simple-console"
        )

        args = config.to_command_args()
        expected = ["--tags", "smoke", "--parallel", "--n", "4", "--env", "dev",
                   "--verbose", "--simple-console", "specs"]
        assert args == expected

    def test_get_environment(self):
        """Test environment variables generation."""
        config = GaugeConfig(
            gauge_root="/opt/gauge",
            environment_variables={"TEST_VAR": "test_value"}
        )

        env = config.get_environment()
        assert "GAUGE_ROOT" in env
        assert env["GAUGE_ROOT"] == "/opt/gauge"
        assert "TEST_VAR" in env
        assert env["TEST_VAR"] == "test_value"


class TestGaugeTask:
    """Test the GaugeTask class."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        task = GaugeTask()
        assert task.config is not None
        assert isinstance(task.config, GaugeConfig)

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = GaugeConfig(specs_dir="custom")
        task = GaugeTask(config)
        assert task.config == config

    @patch('shutil.which')
    def test_find_gauge_executable_in_path(self, mock_which):
        """Test finding gauge executable in PATH."""
        mock_which.return_value = "/usr/bin/gauge"
        task = GaugeTask()

        executable = task._find_gauge_executable()
        assert executable == "/usr/bin/gauge"
        mock_which.assert_called_once_with("gauge")

    @patch('shutil.which')
    def test_find_gauge_executable_in_gauge_root(self, mock_which):
        """Test finding gauge executable in gauge_root."""
        mock_which.return_value = None
        config = GaugeConfig(gauge_root="/opt/gauge")
        task = GaugeTask(config)

        with patch('pathlib.Path.exists', return_value=True):
            executable = task._find_gauge_executable()
            assert executable == "/opt/gauge/bin/gauge"

    @patch('shutil.which')
    def test_find_gauge_executable_not_found(self, mock_which):
        """Test exception when gauge executable is not found."""
        mock_which.return_value = None
        task = GaugeTask()

        with pytest.raises(RuntimeError, match="Gauge executable not found"):
            task._find_gauge_executable()

    @patch('gauge_pybuild_plugin.core.subprocess.run')
    @patch.object(GaugeTask, '_find_gauge_executable')
    def test_run_success(self, mock_find_gauge, mock_subprocess):
        """Test successful gauge run."""
        mock_find_gauge.return_value = "/usr/bin/gauge"
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = "Success"
        mock_subprocess.return_value.stderr = ""

        task = GaugeTask()
        result = task.run()

        assert result is True
        mock_subprocess.assert_called_once()
        call_args = mock_subprocess.call_args[0][0]
        assert call_args[0] == "/usr/bin/gauge"
        assert call_args[1] == "run"

    @patch('gauge_pybuild_plugin.core.subprocess.run')
    @patch.object(GaugeTask, '_find_gauge_executable')
    def test_run_failure(self, mock_find_gauge, mock_subprocess):
        """Test failed gauge run."""
        mock_find_gauge.return_value = "/usr/bin/gauge"
        mock_subprocess.return_value.returncode = 1
        mock_subprocess.return_value.stdout = ""
        mock_subprocess.return_value.stderr = "Error"

        task = GaugeTask()
        result = task.run()

        assert result is False

    @patch('gauge_pybuild_plugin.core.subprocess.run')
    @patch.object(GaugeTask, '_find_gauge_executable')
    def test_validate(self, mock_find_gauge, mock_subprocess):
        """Test gauge validation."""
        mock_find_gauge.return_value = "/usr/bin/gauge"
        mock_subprocess.return_value.returncode = 0

        task = GaugeTask()
        result = task.validate()

        assert result is True
        call_args = mock_subprocess.call_args[0][0]
        assert call_args[0] == "/usr/bin/gauge"
        assert call_args[1] == "validate"

    @patch('gauge_pybuild_plugin.core.subprocess.run')
    @patch.object(GaugeTask, '_find_gauge_executable')
    def test_install_plugin(self, mock_find_gauge, mock_subprocess):
        """Test plugin installation."""
        mock_find_gauge.return_value = "/usr/bin/gauge"
        mock_subprocess.return_value.returncode = 0

        task = GaugeTask()
        result = task.install_plugin("python", "0.3.7")

        assert result is True
        call_args = mock_subprocess.call_args[0][0]
        assert call_args == ["/usr/bin/gauge", "install", "python", "--version", "0.3.7"]

    @patch('gauge_pybuild_plugin.core.subprocess.run')
    @patch.object(GaugeTask, '_find_gauge_executable')
    def test_format_specs(self, mock_find_gauge, mock_subprocess):
        """Test spec formatting."""
        mock_find_gauge.return_value = "/usr/bin/gauge"
        mock_subprocess.return_value.returncode = 0

        task = GaugeTask()
        result = task.format_specs()

        assert result is True
        call_args = mock_subprocess.call_args[0][0]
        assert call_args[0] == "/usr/bin/gauge"
        assert call_args[1] == "format"


class TestGaugePlugin:
    """Test the GaugePlugin class."""

    def test_init_without_config_file(self):
        """Test initialization without configuration file."""
        plugin = GaugePlugin()
        assert plugin.config is not None
        assert isinstance(plugin.config, GaugeConfig)

    def test_create_task(self):
        """Test task creation."""
        plugin = GaugePlugin()
        task = plugin.create_task()

        assert isinstance(task, GaugeTask)
        assert task.config == plugin.config

    def test_create_task_with_override(self):
        """Test task creation with configuration override."""
        plugin = GaugePlugin()
        task = plugin.create_task({"in_parallel": True, "nodes": 4})

        assert isinstance(task, GaugeTask)
        assert task.config.in_parallel is True
        assert task.config.nodes == 4

    @patch.object(GaugeTask, 'run')
    def test_run_specs(self, mock_run):
        """Test running specs through plugin."""
        mock_run.return_value = True
        plugin = GaugePlugin()

        result = plugin.run_specs(in_parallel=True)
        assert result is True
        mock_run.assert_called_once()

    @patch.object(GaugeTask, 'validate')
    def test_validate_project(self, mock_validate):
        """Test project validation through plugin."""
        mock_validate.return_value = True
        plugin = GaugePlugin()

        result = plugin.validate_project()
        assert result is True
        mock_validate.assert_called_once()

    @patch.object(GaugeTask, 'format_specs')
    def test_format_specs(self, mock_format):
        """Test spec formatting through plugin."""
        mock_format.return_value = True
        plugin = GaugePlugin()

        result = plugin.format_specs()
        assert result is True
        mock_format.assert_called_once()
