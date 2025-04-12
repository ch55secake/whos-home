from unittest.mock import patch

from src.executor.nmap_executor import NmapExecutor


class MockFlags:
    SERVICE_SCAN = "-sV"

    AGGRESSIVE = "-A"

    COMMON_PORTS = "-F"

    FULL_PORT_SCAN = "-p-"

    AGGRESSIVE_TIMING = "-T5"

    NORMAL_TIMING = "-T3"

    XML_OUTPUT_TO_STDOUT = "-oX -"  # xml output to terminal

    ICMP_PING = "-PE -PP -PM"  # -PE/PP/PM: ICMP echo, timestamp, and netmask request discovery probes

    ARP_PING = "-PR"  # -PR: ARP ping scan (local network only)

    COMBINED_PING = "-PE -PP -PM -PR"  # -PE/PP/PM/PR: Combined ICMP and ARP ping scan

    EXCLUDE_PORTS = "-sn"  # -sn: No port scan (only host discovery)


@patch("src.executor.nmap_executor.AvailableNmapFlags", MockFlags)
def test_build_quiet_slow_scan():
    executor = NmapExecutor(host="192.168.1.1", cidr="24")
    expected_command = "nmap -F -T3 -oX 192.168.1.1/24"
    assert executor.build_quiet_slow_scan() == expected_command


@patch("src.executor.nmap_executor.AvailableNmapFlags", MockFlags)
def test_build_aggressive_privileged_os_scan():
    executor = NmapExecutor(host="10.0.0.1", cidr="16")
    expected_command = "sudo nmap -F -T4 -O -oX 10.0.0.1/16"
    assert executor.build_aggressive_privileged_scan() == expected_command
