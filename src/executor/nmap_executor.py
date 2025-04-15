from __future__ import annotations

from enum import Enum

from src.data.command_result import CommandResult
from src.executor.default_executor import DefaultExecutor, running_as_sudo


class AvailableNmapFlags(Enum):
    # Need max to add his sweaty little flags
    # :)
    # Wholesome

    """
    Available Nmap flags for building commands
    """
    SERVICE_SCAN = "-sV"

    AGGRESSIVE = "-A"

    OS_DETECTION = "-O"

    COMMON_PORTS = "-F"

    FULL_PORT_SCAN = "-p-"

    AGGRESSIVE_TIMING = "-T5"

    NORMAL_TIMING = "-T3"

    XML_OUTPUT_TO_STDOUT = "-oX -"  # xml output to terminal

    ICMP_PING = "-PE -PP -PM"  # -PE/PP/PM: ICMP echo, timestamp, and netmask request discovery probes

    ARP_PING = "-PR"  # -PR: ARP ping scan (local network only)

    COMBINED_PING = "-PE -PP -PM -PR"  # -PE/PP/PM/PR: Combined ICMP and ARP ping scan

    EXCLUDE_PORTS = "-sn"  # -sn: No port scan (only host discovery)


class NmapCommandBuilder:
    def __init__(self, host: str, cidr: str, sudo: bool = False) -> None:
        self.host = host
        self.cidr = cidr
        self.sudo = sudo
        self.enabled_flags = set()

    def enable_flag(self, flag: AvailableNmapFlags) -> NmapCommandBuilder:
        self.enabled_flags.add(flag)
        return self

    def disable_flag(self, flag: AvailableNmapFlags) -> NmapCommandBuilder:
        self.enabled_flags.discard(flag)
        return self

    def set_flag(self, flag: AvailableNmapFlags, is_enabled: bool) -> NmapCommandBuilder:
        return self.enable_flag(flag) if is_enabled else self.disable_flag(flag)

    def enable_exclude_ports(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.EXCLUDE_PORTS)

    def enable_aggressive_timing(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.AGGRESSIVE_TIMING)

    def enable_service_discovery(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.SERVICE_SCAN)

    def enable_aggressive(self) -> NmapCommandBuilder:
        """
        If you are going to use this the code needs to handle port scanning, or this throws errors
        :return: NmapCommandBuilder
        """
        return self.enable_flag(AvailableNmapFlags.AGGRESSIVE)

    def enable_os_detection(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.OS_DETECTION)

    def enable_icmp_ping(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.ICMP_PING)

    def enable_arp_ping(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.ARP_PING)

    def enable_xml_output(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.XML_OUTPUT_TO_STDOUT)

    def set_sudo(self) -> NmapCommandBuilder:
        self.sudo = True
        return self

    def build(self) -> str:
        flags = " ".join(flag.value for flag in self.enabled_flags)
        return f"{"sudo" if self.sudo else ""} nmap {flags} {self.host}/{self.cidr}"

    def build_version_command(self) -> str:
        return f"{"sudo" if self.sudo else ""} nmap --version"


class NmapExecutor:
    """
    Uses DefaultExecutor to execute nmap commands
    """

    def __init__(self, host: str, cidr: str, timeout: float = 60) -> None:
        """
        Executor for nmap commands will provide network scan
        :param host: list of hosts to execute scans on
        :param cidr: ip range to execute scans on
        :param timeout: timeout of command execution in seconds
        """
        self.host = host
        self.cidr = cidr
        self.timeout = timeout
        self.executor = DefaultExecutor(timeout=self.timeout)
        self.privileged = running_as_sudo()
        self.builder = NmapCommandBuilder(host, cidr, self.privileged)

    def execute_version_command(self) -> CommandResult:
        """
        Executes a version command to check the nmap if the nmap installation is present
        :return: result of command execution
        """
        command: str = self.builder.build_version_command()
        return self.executor.execute(command)

    def execute_icmp_host_discovery(self) -> CommandResult:
        """
        Execute a host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_service_discovery()
            .enable_exclude_ports()
            .enable_aggressive_timing()
            .enable_icmp_ping()
            .enable_xml_output()
            .build()
        )
        return self.executor.execute(command)

    def execute_arp_host_discovery(self) -> CommandResult:
        """
        Execute an arp host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_service_discovery()
            .enable_exclude_ports()
            .enable_aggressive_timing()
            .enable_arp_ping()
            .enable_xml_output()
            .build()
        )
        return self.executor.execute(command)

    def execute_arp_icmp_host_discovery(self) -> CommandResult:
        """
        Execute an arp/icmp host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder
            # .enable_os_detection()
            .enable_service_discovery()
            .enable_exclude_ports()
            # .enable_flag(AvailableNmapFlags.COMMON_PORTS)
            .enable_aggressive_timing()
            .enable_icmp_ping()
            .enable_arp_ping()
            .enable_xml_output()
            .build()
        )
        return self.executor.execute(command)

    def execute_passive_scan(self) -> CommandResult:
        """
        Executes a more passive host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_flag(AvailableNmapFlags.COMMON_PORTS)
            .enable_flag(AvailableNmapFlags.SERVICE_SCAN)
            .enable_flag(AvailableNmapFlags.NORMAL_TIMING)
            .enable_xml_output()
            .build()
        )
        return self.executor.execute(command)

    def execute_aggressive_scan(self) -> CommandResult:
        """
        Run an aggressive nmap port scan
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_flag(AvailableNmapFlags.COMMON_PORTS)
            .enable_aggressive_timing()
            .enable_flag(AvailableNmapFlags.AGGRESSIVE)
            .enable_xml_output()
            .build()
        )
        return self.executor.execute(command)
