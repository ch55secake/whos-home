from __future__ import annotations

from enum import Enum


class AvailableNmapFlags(Enum):
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
        If you are going to use this, the code needs to handle port scanning, or this throws errors
        :return: NmapCommandBuilder
        """
        return self.enable_flag(AvailableNmapFlags.AGGRESSIVE)

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

    def build(self) -> str:
        flags = " ".join(flag.value for flag in self.enabled_flags)
        return f"{"sudo" if self.sudo else ""} nmap {flags} {self.host}/{self.cidr}"

    def build_without_cidr(self) -> str:
        flags = " ".join(flag.value for flag in self.enabled_flags)
        return f"{"sudo" if self.sudo else ""} nmap {flags} {self.host}"

    def build_version_command(self) -> str:
        return f"{"sudo" if self.sudo else ""} nmap --version"
