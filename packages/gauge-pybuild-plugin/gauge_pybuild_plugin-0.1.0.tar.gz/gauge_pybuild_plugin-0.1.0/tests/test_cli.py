"""
Tests for the CLI interface.
"""

from unittest.mock import Mock, patch

from click.testing import CliRunner

from gauge_pybuild_plugin.cli import cli


class TestCLI:
    """Test the CLI interface."""

    def test_cli_help(self):
        """Test CLI help output."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])

        assert result.exit_code == 0
        assert "Gauge Python Build Plugin" in result.output
        assert "run" in result.output
        assert "validate" in result.output
        assert "format" in result.output
        assert "install" in result.output
        assert "config" in result.output

    @patch('gauge_pybuild_plugin.cli.GaugePlugin')
    def test_run_command_basic(self, mock_plugin_class):
        """Test basic run command."""
        mock_plugin = Mock()
        mock_task = Mock()
        mock_task.run.return_value = True
        mock_plugin.create_task.return_value = mock_task
        mock_plugin_class.return_value = mock_plugin

        runner = CliRunner()
        result = runner.invoke(cli, ['run'])

        assert result.exit_code == 0
        assert "completed successfully" in result.output
        mock_task.run.assert_called_once_with(None)

    @patch('gauge_pybuild_plugin.cli.GaugePlugin')
    def test_run_command_with_options(self, mock_plugin_class):
        """Test run command with various options."""
        mock_plugin = Mock()
        mock_task = Mock()
        mock_task.run.return_value = True
        mock_plugin.create_task.return_value = mock_task
        mock_plugin_class.return_value = mock_plugin

        runner = CliRunner()
        result = runner.invoke(cli, [
            'run',
            '--specs-dir', 'custom_specs',
            '--tags', 'smoke',
            '--parallel',
            '--nodes', '4',
            '--env', 'dev',
            '--additional-flags', '--verbose',
            'spec1.spec', 'spec2.spec'
        ])

        assert result.exit_code == 0
        mock_plugin.create_task.assert_called_once()

        # Check the configuration passed to create_task
        config_dict = mock_plugin.create_task.call_args[0][0]
        assert config_dict['specs_dir'] == 'custom_specs'
        assert config_dict['tags'] == 'smoke'
        assert config_dict['in_parallel'] is True
        assert config_dict['nodes'] == 4
        assert config_dict['env'] == 'dev'
        assert config_dict['additional_flags'] == '--verbose'

        # Check the specs passed to run
        mock_task.run.assert_called_once_with(['spec1.spec', 'spec2.spec'])

    @patch('gauge_pybuild_plugin.cli.GaugePlugin')
    def test_run_command_failure(self, mock_plugin_class):
        """Test run command failure."""
        mock_plugin = Mock()
        mock_task = Mock()
        mock_task.run.return_value = False
        mock_plugin.create_task.return_value = mock_task
        mock_plugin_class.return_value = mock_plugin

        runner = CliRunner()
        result = runner.invoke(cli, ['run'])

        assert result.exit_code == 1
        assert "execution failed" in result.output

    @patch('gauge_pybuild_plugin.cli.GaugePlugin')
    def test_validate_command(self, mock_plugin_class):
        """Test validate command."""
        mock_plugin = Mock()
        mock_task = Mock()
        mock_task.validate.return_value = True
        mock_plugin.create_task.return_value = mock_task
        mock_plugin_class.return_value = mock_plugin

        runner = CliRunner()
        result = runner.invoke(cli, ['validate', '--specs-dir', 'custom_specs'])

        assert result.exit_code == 0
        assert "validation completed successfully" in result.output
        mock_task.validate.assert_called_once()

    @patch('gauge_pybuild_plugin.cli.GaugePlugin')
    def test_format_command(self, mock_plugin_class):
        """Test format command."""
        mock_plugin = Mock()
        mock_task = Mock()
        mock_task.format_specs.return_value = True
        mock_plugin.create_task.return_value = mock_task
        mock_plugin_class.return_value = mock_plugin

        runner = CliRunner()
        result = runner.invoke(cli, ['format'])

        assert result.exit_code == 0
        assert "formatting completed successfully" in result.output
        mock_task.format_specs.assert_called_once()

    @patch('gauge_pybuild_plugin.cli.GaugePlugin')
    def test_install_command(self, mock_plugin_class):
        """Test install command."""
        mock_plugin = Mock()
        mock_task = Mock()
        mock_task.install_plugin.return_value = True
        mock_plugin.create_task.return_value = mock_task
        mock_plugin_class.return_value = mock_plugin

        runner = CliRunner()
        result = runner.invoke(cli, ['install', 'python', '--version', '0.3.7'])

        assert result.exit_code == 0
        assert "installed successfully" in result.output
        mock_task.install_plugin.assert_called_once_with('python', '0.3.7')

    def test_config_show_no_config(self):
        """Test config show with no configuration."""
        runner = CliRunner()
        result = runner.invoke(cli, ['config', '--show'])

        assert result.exit_code == 0
        assert "No Gauge configuration found" in result.output

    def test_config_init(self):
        """Test config initialization."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(cli, ['config', '--init'])

            assert result.exit_code == 0
            assert "Initialized gauge configuration" in result.output

            # Check that pyproject.toml was created
            with open('pyproject.toml') as f:
                content = f.read()
                assert '[tool.gauge]' in content
                assert 'specs_dir = "specs"' in content

    def test_config_init_existing_file(self):
        """Test config initialization with existing file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # Create existing pyproject.toml
            with open('pyproject.toml', 'w') as f:
                f.write('[tool.poetry]\nname = "test"\n')

            result = runner.invoke(cli, ['config', '--init'])

            assert result.exit_code == 0
            assert "already exists" in result.output

    def test_verbose_option(self):
        """Test verbose option."""
        runner = CliRunner()
        with patch('gauge_pybuild_plugin.cli.GaugePlugin') as mock_plugin_class:
            mock_plugin = Mock()
            mock_task = Mock()
            mock_task.run.return_value = True
            mock_plugin.create_task.return_value = mock_task
            mock_plugin_class.return_value = mock_plugin

            result = runner.invoke(cli, ['--verbose', 'run'])

            assert result.exit_code == 0
            assert "Running Gauge with configuration" in result.output
