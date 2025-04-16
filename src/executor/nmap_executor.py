from __future__ import annotations

import os
from enum import Enum

from src.data.command_result import CommandResult
from src.executor.default_executor import DefaultExecutor, running_as_sudo
from src.util.logger import Logger


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

    TOP_1000_PORTS = "--top-ports=1000"

    FULL_PORT_SCAN = "-p-"

    AGGRESSIVE_TIMING = "-T5"

    NORMAL_TIMING = "-T3"

    XML_OUTPUT_TO_STDOUT = "-oX -"  # xml output to terminal

    ICMP_PING = "-PE -PP -PM"  # -PE/PP/PM: ICMP echo, timestamp, and netmask request discovery probes

    ARP_PING = "-PR"  # -PR: ARP ping scan (local network only)

    COMBINED_PING = "-PE -PP -PM -PR"  # -PE/PP/PM/PR: Combined ICMP and ARP ping scan

    EXCLUDE_PORTS = "-sn"  # -sn: No port scan (only host discovery)

    SKIP_HOST_DISCOVERY = "-Pn"  # -Pn: Skip host discovery (assume all hosts are up

    OUTPUT_TO_XML_FILE = "-oX"


class NmapCommandBuilder:
    def __init__(self, host: str, cidr: str, sudo: bool = False) -> None:
        self.host = host
        self.cidr = cidr
        self.sudo = sudo
        self.enabled_flags = set()

    def disable_all_flags(self) -> NmapCommandBuilder:
        """
        Clear all flags
        :return: NmapCommandBuilder
        """
        self.enabled_flags.clear()
        return self

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

    def enable_service_scan(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.SERVICE_SCAN)

    def enable_aggressive(self) -> NmapCommandBuilder:
        """
        If you are going to use this the code needs to handle port scanning, or this throws errors
        :return: NmapCommandBuilder
        """
        return self.enable_flag(AvailableNmapFlags.AGGRESSIVE)

    def enable_top_1000_ports(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.TOP_1000_PORTS)

    def enable_skip_host_discovery(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.SKIP_HOST_DISCOVERY)

    def enable_os_detection(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.OS_DETECTION)

    def enable_icmp_ping(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.ICMP_PING)

    def enable_arp_ping(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.ARP_PING)

    def enable_xml_to_stdout(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.XML_OUTPUT_TO_STDOUT)

    def enable_output_to_xml_file(self) -> NmapCommandBuilder:
        return self.enable_flag(AvailableNmapFlags.OUTPUT_TO_XML_FILE)

    def set_sudo(self) -> NmapCommandBuilder:
        self.sudo = True
        return self

    def build_host_discovery_command(self) -> str:
        flags = " ".join(flag.value for flag in self.enabled_flags)
        return f"{"sudo" if self.sudo else ""} nmap {flags} {self.host}/{self.cidr}"

    def build_version_command(self) -> str:
        return f"{"sudo" if self.sudo else ""} nmap --version"

    def build_port_scan_command(self) -> str:
        flags = " ".join(flag.value for flag in self.enabled_flags)
        os.makedirs('output', exist_ok=True)  # move this somewhere else if you want

        return (f"cat ip_list.txt | xargs -I % -P 20 {"sudo " if self.sudo else ""}nmap % {flags} "
                f"{AvailableNmapFlags.OUTPUT_TO_XML_FILE.value} output/nmap-general-port-scan-%.xml")


class NmapExecutor:
    """
    Uses DefaultExecutor to execute nmap commands
    """

    def __init__(self, host: str, cidr: str, timeout: float = 120) -> None:
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
            self.builder.enable_service_scan()
            .enable_exclude_ports()
            .enable_aggressive_timing()
            .enable_icmp_ping()
            .enable_xml_to_stdout()
            .build_host_discovery_command()
        )
        return self.executor.execute_host_discovery_command(command)

    def execute_arp_host_discovery(self) -> CommandResult:
        """
        Execute an arp host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_service_scan()
            .enable_exclude_ports()
            .enable_aggressive_timing()
            .enable_arp_ping()
            .enable_xml_to_stdout()
            .build_host_discovery_command()
        )
        return self.executor.execute_host_discovery_command(command)

    def execute_arp_icmp_host_discovery(self) -> CommandResult:
        """
        Execute an arp and icmp host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_exclude_ports()
            .enable_aggressive_timing()
            .enable_icmp_ping()
            .enable_arp_ping()
            .enable_xml_to_stdout()
            .build_host_discovery_command()
        )
        return self.executor.execute_host_discovery_command(command)

    def execute_general_port_scan(self) -> CommandResult:
        """
        Executes a general port scan designed for the home network. Should come out as 'nmap -sV -T5 --top-ports=1000 -Pn -oX -'
        :return: result of command execution
        """
        self.builder.disable_all_flags()
        # cat targets.txt | xargs -I % -P 10 sudo nmap % -sV --top-ports=1000 -Pn -T5 %
        command: str = (
            self.builder.enable_top_1000_ports()
            .enable_service_scan()
            .enable_aggressive_timing()
            .enable_skip_host_discovery()
            .build_port_scan_command()
        )
        Logger().debug(f"Running following command: {command}")
        return self.executor.execute_port_scan_command(command)

    def execute_aggressive_scan(self) -> CommandResult:
        """
        Run an aggressive nmap port scan
        :return: result of command execution
        """
        # This needs further consideration in the future - do we want/need an agro scan in a home network?
        # Do we want even more options? do we want fully customisable port scans?
        # For now this is a placeholder and is not used.
        command: str = (
            self.builder.enable_flag(AvailableNmapFlags.TOP_1000_PORTS)
            .enable_aggressive_timing()
            .enable_flag(AvailableNmapFlags.AGGRESSIVE)
            .enable_xml_to_stdout()
            .build_host_discovery_command()
        )
        return self.executor.execute_host_discovery_command(command)
