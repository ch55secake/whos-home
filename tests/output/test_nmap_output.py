import pytest

from src.data.command_result import CommandResult
from src.data.device import Device
from src.data.scan_result import ScanResult
from src.output.nmap_output import (
    format_and_output,
    build_ip_message,
    build_mac_addr_message,
    get_ip_and_mac_message,
    get_number_of_unique_devices,
    get_unique_devices_message,
    get_host_totals_message,
    format_and_output_from_check,
)


@pytest.fixture
def test_devices():
    return [
        Device(ip_addr="192.168.0.1", mac_addr="00:11:22:33:44:55", hostname="router"),
        Device(ip_addr="192.168.0.2", mac_addr=None, hostname="laptop"),
        Device(ip_addr="192.168.0.3", mac_addr="AA:BB:CC:DD:EE:FF", hostname="phone"),
        Device(ip_addr="192.168.0.4", mac_addr="11:22:33:44:55:66", hostname="router"),
    ]


@pytest.fixture
def scan_result_mock():
    class DummyScanResult(ScanResult):
        def get_hosts_up_from_runstats(self):
            return 3

        def get_total_hosts_from_runstats(self):
            return 4

    return DummyScanResult(run_stats={}, hosts=[])


def test_build_ip_message():
    device = Device(ip_addr="192.168.0.10", mac_addr=None, hostname="test-device", os=None, ports=None)
    msg = build_ip_message(device)
    assert "192.168.0.10" in msg


def test_build_mac_addr_message_with_mac():
    device = Device(ip_addr="x", mac_addr="AA:BB:CC", hostname="host", os=None, ports=None)
    msg = build_mac_addr_message(device)
    assert "AA:BB:CC" in msg


def test_build_mac_addr_message_without_mac():
    device = Device(ip_addr="x", mac_addr=None, hostname="host", os=None, ports=None)
    msg = build_mac_addr_message(device)
    assert msg is None


def test_get_ip_and_mac_message_with_mac():
    device = Device(ip_addr="1.2.3.4", mac_addr="00:00:00", hostname="abc", os=None, ports=None)
    msg = get_ip_and_mac_message(device)
    assert "1.2.3.4" in msg
    assert "00:00:00" in msg
    assert "abc" in msg


def test_get_ip_and_mac_message_without_mac():
    device = Device(ip_addr="1.2.3.4", mac_addr=None, hostname="abc", os=None, ports=None)
    msg = get_ip_and_mac_message(device)
    assert "1.2.3.4" in msg
    assert "abc" in msg
    assert "mac" not in msg.lower()


def test_get_number_of_unique_devices(test_devices):
    count = get_number_of_unique_devices(test_devices)
    assert count == 4


def test_get_unique_devices_message(test_devices):
    msg = get_unique_devices_message(test_devices)
    assert "4" in msg
    assert "unique devices" in msg


def test_get_host_totals_message(scan_result_mock):
    msg = get_host_totals_message(scan_result_mock)
    assert "2" in msg
    assert "4" in msg


def test_format_and_output_prints_expected(test_devices, scan_result_mock, capsys):
    format_and_output(scan_result_mock, test_devices)
    captured = capsys.readouterr()
    assert "Found ip address" in captured.out
    assert "✔️ Scan suggests that you have" in captured.out
    assert "✔️ It also found" in captured.out


def test_format_and_output_from_check_found_version(capsys):
    result = CommandResult(
        command="command",
        success=True,
        stderr="",
        stdout="Nmap version 7.95",
        return_code=0,
    )

    format_and_output_from_check(result)
    captured = capsys.readouterr()

    assert "7.95" in captured.out


def test_format_and_output_from_check_not_found(capsys):
    result = CommandResult(
        command="command",
        success=False,
        stderr="",
        stdout="",
        return_code=0,
    )

    format_and_output_from_check(result)
    captured = capsys.readouterr()

    assert "ERROR" in captured.out
