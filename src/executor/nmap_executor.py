from __future__ import annotations
from enum import Enum

from src.data.command_result import CommandResult
from src.executor.default_executor import DefaultExecutor

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


class NmapCommandBuilder:
    def __init__(self, host, cidr) -> None:
        self.host = host
        self.cidr = cidr
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

    def enable_icmp_ping(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.ICMP_PING)

    def enable_arp_ping(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.ARP_PING)

    def enable_xml_output(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.XML_OUTPUT_TO_STDOUT)

    def build(self) -> str:
        flags = ' '.join(flag.value for flag in self.enabled_flags)
        return f"nmap {flags} {self.host}/{self.cidr}"

class NmapExecutor:
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
        :return: result of command execution
        """
        command: str = (NmapCommandBuilder(self.host, self.cidr)
                        .enable_exclude_ports()
                        .enable_aggressive_timing()
                        .enable_icmp_ping()
                        .enable_xml_output()
                        .build())
        return self.executor.execute(command)

    def execute_arp_host_discovery(self) -> CommandResult:
        """
        Execute an arp host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (NmapCommandBuilder(self.host, self.cidr)
                        .enable_exclude_ports()
                        .enable_aggressive_timing()
                        .enable_arp_ping()
                        .enable_xml_output()
                        .build())
        return self.executor.execute(command)

    def execute_arp_icmp_host_discovery(self) -> CommandResult:
        """
        Execute an arp/icmp host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (NmapCommandBuilder(self.host, self.cidr)
                        .enable_exclude_ports()
                        .enable_aggressive_timing()
                        .enable_icmp_ping()
                        .enable_arp_ping()
                        .enable_xml_output()
                        .build())
        return self.executor.execute(command)


    def execute_passive_scan(self) -> CommandResult:
        """
        Executes a more passive host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (NmapCommandBuilder(self.host, self.cidr)
                        .enable_flag(AvailableNmapFlags.COMMON_PORTS)
                        .enable_flag(AvailableNmapFlags.SERVICE_SCAN)
                        .enable_flag(AvailableNmapFlags.NORMAL_TIMING)
                        .enable_xml_output()
                        .build())
        return self.executor.execute(command)

    def execute_aggressive_scan(self) -> CommandResult:
        """
        Run an aggressive nmap port scan
        :return: result of command execution
        """
        command: str = (NmapCommandBuilder(self.host, self.cidr)
                        .enable_flag(AvailableNmapFlags.COMMON_PORTS)
                        .enable_aggressive_timing()
                        .enable_flag(AvailableNmapFlags.AGGRESSIVE)
                        .enable_xml_output()
                        .build())
        return self.executor.execute(command)
