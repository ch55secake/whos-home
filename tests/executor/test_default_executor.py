import subprocess

from unittest.mock import patch, MagicMock

from src.executor.default_executor import DefaultExecutor, running_as_sudo
from src.data.command_result import CommandResult


@patch("src.executor.default_executor.running_as_sudo", return_value=False)
@patch("src.executor.default_executor.subprocess.run")
def test_execute_warns_if_not_sudo(mock_subprocess, mock_sudo, capsys):
    mock_subprocess.return_value = MagicMock(
        stdout="output",
        stderr="",
        returncode=0,
    )

    executor = DefaultExecutor(timeout=5, warn_about_sudo=True)
    result = executor.execute("echo 'test'")

    assert isinstance(result, CommandResult)
    assert result.stdout == "output"
    captured = capsys.readouterr()
    assert "Warning" in captured.out


@patch("src.executor.default_executor.running_as_sudo", return_value=True)
@patch("src.executor.default_executor.subprocess.run")
def test_execute_success(mock_subprocess, mock_sudo):
    mock_subprocess.return_value = MagicMock(
        stdout="success output",
        stderr="",
        returncode=0,
    )

    executor = DefaultExecutor(timeout=5)
    result = executor.execute("echo 'test'")
    assert result.stdout == "success output"
    assert result.success is True
    assert result.return_code == 0


@patch("src.executor.default_executor.running_as_sudo", return_value=True)
@patch("src.executor.default_executor.subprocess.run", side_effect=subprocess.CalledProcessError(00, "bad"))
def test_execute_failure(mock_subprocess, mock_sudo, capsys):
    executor = DefaultExecutor(timeout=5)
    result = executor.execute("badcommand")

    assert isinstance(result, CommandResult)
    assert result.success == ""
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.return_code == ""

    captured = capsys.readouterr()
    assert "error occurred" in captured.out


@patch("src.executor.default_executor.os.getuid", return_value=0)
def test_running_as_sudo_true(mock_getuid):
    assert running_as_sudo() is True


@patch("src.executor.default_executor.os.getuid", return_value=1000)
def test_running_as_sudo_false(mock_getuid):
    assert running_as_sudo() is False
