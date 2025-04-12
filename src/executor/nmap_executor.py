from enum import Enum

from src.data.command_result import CommandResult
from src.executor.default_executor import DefaultExecutor


class NmapExecutor(object):

    def __init__(self, host: str, cidr: str, timeout: float = 60) -> None:
        """
        Executor for nmap commands will provide network scan
        :param host: list of hosts to execute scans on
        :param cidr: ip range to execute scans on
        """
        self.host = host
        self.cidr = cidr
        self.timeout = timeout
        self.executor = DefaultExecutor(timeout=self.timeout)


    def execute_icmp_host_discovery(self) -> CommandResult:
        """
        Execute a host discovery scan using nmap
        :return:
        """
        command: str = self.build_icmp_host_discovery_scan()
        return self.executor.execute(command)

    def execute_passive_scan(self) -> CommandResult:
        """
        Executes a more passive host discovery scan using nmap
        :return:
        """
        command: str = self.build_quiet_slow_scan()
        return self.executor.execute(command)

    def execute_aggressive_scan(self) -> CommandResult:
        """
        Run an aggressive nmap port scan
        :return:
        """
        command: str = self.build_aggressive_privileged_scan()
        return self.executor.execute(command)


    def build_icmp_host_discovery_scan(self) -> str:
        """
        Build a host discovery scan using nmap
        :returns: The command as a string
        """
        return (f"nmap {AvailableNmapFlags.EXCLUDE_PORTS.value} "
                f"{AvailableNmapFlags.AGGRESSIVE_TIMING.value} "
                f"{AvailableNmapFlags.ICMP_PING.value} "
                f"{AvailableNmapFlags.XML_OUTPUT_TO_STDOUT.value} "
                f"{self.host}/{self.cidr}")

    def build_quiet_slow_scan(self) -> str:
        """
        Build a quiet slow scan will only scan over common ports with normal timing
        :return: nmap command as a string
        """
        return (f"nmap {AvailableNmapFlags.COMMON_PORTS.value} "
                f"{AvailableNmapFlags.SERVICE_SCAN.value} "
                f"{AvailableNmapFlags.NORMAL_TIMING.value} "
                f"{AvailableNmapFlags.XML_OUTPUT_TO_STDOUT.value} "
                f"{self.host}/{self.cidr}")

    def build_aggressive_privileged_scan(self) -> str:
        """
        Build an aggressive privileged port scan using the -A argument but will only scan over
        common ports
        :return: nmap command as a string
        """
        return (f"sudo nmap {AvailableNmapFlags.COMMON_PORTS.value} "
                f"{AvailableNmapFlags.SERVICE_SCAN.value} "
                f"{AvailableNmapFlags.AGGRESSIVE_TIMING.value} "
                f"{AvailableNmapFlags.AGGRESSIVE.value} "
                f"{AvailableNmapFlags.XML_OUTPUT_TO_STDOUT.value} "
                f"{self.host}/{self.cidr}")


class AvailableNmapFlags(Enum):
    # Need max to add his sweaty little flags
    # :)
    # Wholesome

    """
    Available Nmap flags for building commands
    """
    SERVICE_SCAN = "-sV"

    AGGRESSIVE = "-A"

    COMMON_PORTS = "-F"

    FULL_PORT_SCAN = "-p-"

    AGGRESSIVE_TIMING = "-T5"

    NORMAL_TIMING = "-T3"

    XML_OUTPUT_TO_STDOUT = "-oX -" # xml output to terminal

    ICMP_PING = "-PE -PP -PM" # -PE/PP/PM: ICMP echo, timestamp, and netmask request discovery probes

    ARP_PING = "-PR" # -PR: ARP ping scan (local network only)

    COMBINED_PING = "-PE -PP -PM -PR" # -PE/PP/PM/PR: Combined ICMP and ARP ping scan

    EXCLUDE_PORTS = "-sn" # -sn: No port scan (only host discovery)
