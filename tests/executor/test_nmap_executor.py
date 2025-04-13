from unittest.mock import patch, MagicMock
import pytest

from src.executor.nmap_executor import NmapCommandBuilder, NmapExecutor, AvailableNmapFlags


@pytest.fixture
def test_nmap_builder():
    return NmapCommandBuilder("192.168.1.0", "24")


def test_builder_adds_flags_correctly(test_nmap_builder):
    test_nmap_builder.enable_aggressive().enable_service_discovery().enable_arp_ping()
    command = test_nmap_builder.build()
    assert "-A" in command
    assert "-sV" in command
    assert "-PR" in command
    assert "nmap" in command


def test_builder_sets_sudo():
    builder = NmapCommandBuilder("10.0.0.1", "16").set_sudo()
    command = builder.build()
    assert command.startswith("sudo")


def test_builder_disable_flag():
    builder = NmapCommandBuilder("127.0.0.1", "8")
    builder.enable_aggressive().disable_flag(AvailableNmapFlags.AGGRESSIVE)
    command = builder.build()
    assert "-A" not in command


@patch("src.executor.nmap_executor.DefaultExecutor")
@patch("src.executor.nmap_executor.running_as_sudo", return_value=False)
def test_execute_icmp_host_discovery(mock_sudo, mock_executor):
    mock_result = MagicMock()
    mock_result.stdout = "<xml>output</xml>"
    mock_executor.return_value.execute.return_value = mock_result

    executor = NmapExecutor("192.168.1.0", "24")
    result = executor.execute_icmp_host_discovery()

    assert mock_executor.called
    assert result.stdout == "<xml>output</xml>"
    cmd = mock_executor.return_value.execute.call_args[0][0]
    assert "-sV" in cmd
    assert "-sn" in cmd
    assert "-T5" in cmd
    assert "-PE" in cmd
    assert "-oX" in cmd


@patch("src.executor.nmap_executor.DefaultExecutor")
@patch("src.executor.nmap_executor.running_as_sudo", return_value=True)
def test_execute_aggressive_scan(mock_sudo, mock_executor):
    mock_result = MagicMock()
    mock_executor.return_value.execute.return_value = mock_result

    executor = NmapExecutor("10.0.0.1", "24")
    result = executor.execute_aggressive_scan()

    assert result == mock_result
    cmd = mock_executor.return_value.execute.call_args[0][0]
    assert "-A" in cmd
    assert "-T5" in cmd
    assert "-F" in cmd
