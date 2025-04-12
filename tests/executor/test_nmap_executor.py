from unittest.mock import patch

from src.executor.nmap_executor import NmapExecutor

class MockFlags:
    COMMON_PORTS = "-F"
    NORMAL_TIMING = "-T3"
    AGGRESSIVE_TIMING = "-T4"
    OS_DETECTION = "-O"
    XML_OUTPUT_TO_STDOUT = "-oX"

@patch('src.executor.nmap_executor.AvailableNmapFlags', MockFlags)
def test_build_quiet_slow_scan():
    executor = NmapExecutor(host="192.168.1.1", ranges="24")
    expected_command = "nmap -F -T3 -oX 192.168.1.1/24"
    assert executor.build_quiet_slow_scan() == expected_command

@patch('src.executor.nmap_executor.AvailableNmapFlags', MockFlags)
def test_build_aggressive_privileged_os_scan():
    executor = NmapExecutor(host="10.0.0.1", ranges="16")
    expected_command = "sudo nmap -F -T4 -O -oX 10.0.0.1/16"
    assert executor.build_aggressive_privileged_scan() == expected_command
