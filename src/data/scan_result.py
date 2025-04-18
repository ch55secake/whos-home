from __future__ import annotations

from dataclasses import dataclass
from typing import OrderedDict, Any, Tuple, Optional

from src.data.device import Device, OperatingSystem, Port, Service


@dataclass
class ScanResult:
    """
    Class to represent the result of a scan.
    """

    run_stats: OrderedDict[str, Any]
    hosts: list[dict] | dict

    def get_os_info_for_host(self) -> dict | None:
        """
        Get the OS info for the host.
        :return: dictionary of the matching os info, or None if not found.
        """
        if self.hosts is not None:
            return self.hosts.get("os", {}).get("osmatch", {})
        return None

    def get_os_name_for_host(self) -> Optional[str]:
        """
        Get the name of the OS running on the host.
        :return: string of os name, or "(Unknown)" if not found.
        """
        os_info = self.get_os_info_for_host()
        if isinstance(os_info, list) and os_info:
            return os_info[0].get("@name", "(Unknown)")
        if isinstance(os_info, dict):
            return os_info.get("@name", "(Unknown)")
        return "(Unknown)"

    def get_os_vendor_to_family(self) -> Tuple[str, str]:
        """
        Create a tuple of the vendor and family of the OS running on the host. Will default to (Unknown, Unknown)
        if not found.
        :return:
        """
        os_info = self.get_os_info_for_host()

        if isinstance(os_info, list) and os_info:
            osclass = os_info[0].get("osclass")
        elif isinstance(os_info, dict):
            osclass = os_info.get("osclass")
        else:
            return "(Unknown)", "(Unknown)"

        if isinstance(osclass, list) and osclass:
            return osclass[0].get("@vendor", "(Unknown)"), osclass[0].get("@osfamily", "(Unknown)")
        if isinstance(osclass, dict):
            return osclass.get("@vendor", "(Unknown)"), osclass.get("@osfamily", "(Unknown)")

        return "(Unknown)", "(Unknown)"

    def get_os_vendor(self) -> str:
        """
        Get the vendor of the OS running on the host.
        :return: string of os vendor name, or "(Unknown)" if not found.
        """
        os_info = self.get_os_info_for_host()
        osclass = os_info.get("osclass") if isinstance(os_info, dict) else {}
        return osclass.get("@vendor", "(Unknown)")

    def get_os_family(self) -> str:
        """
        Return the OS family running on the host.
        :return: string of os family name, or "(Unknown)" if not found.
        """
        os_info = self.get_os_info_for_host()
        osclass = os_info.get("osclass") if isinstance(os_info, dict) else {}
        return osclass.get("@osfamily", "(Unknown)")

    def get_port_id_to_service_name(self) -> dict[str, str]:
        """
        Create a dictionary mapping port IDs to service names.
        :return: port_id_to_service_name: dict[str, str]
        """
        ports = self.hosts.get("ports", {}).get("port", [])
        if isinstance(ports, dict):
            ports = [ports]
        return {
            port.get("@portid", ""): port.get("service", {}).get("@product", "")
            for port in ports
            if isinstance(port, dict)
        }

    def get_port_id_to_protocol(self) -> dict[str, str]:
        """
        Create a dictionary mapping port IDs to protocols.
        :return: port_id_to_protocol: dict[str, str]
        """
        ports = self.hosts.get("ports", {}).get("port", [])
        if isinstance(ports, dict):
            ports = [ports]
        return {port.get("@portid", ""): port.get("@protocol", "") for port in ports if isinstance(port, dict)}

    def get_hosts_up_from_runstats(self) -> int:
        """
        Pull host info of the run stats
        :return: number of hosts up as string
        """
        return int(self.run_stats["hosts"]["@up"])

    def get_total_hosts_from_runstats(self) -> str:
        """
        Pull the total number of hosts from the run stats
        :return: total number of hosts up as a string
        """
        return self.run_stats["hosts"]["@total"]

    def get_address(self, i, address_type: str) -> Any | None:
        """
        Get the address from the scan result based on type
        :return: The address
        """
        addresses = self.hosts[i]["address"] if isinstance(self.hosts, list) else self.hosts["address"]
        if isinstance(addresses, dict):
            addresses = [addresses]

        for address in addresses:
            if address["@addrtype"] == address_type:
                return address["@addr"]
        return None

    def find_hostname(self, i: int) -> Any | None:
        """
        Get the hostname from the scan result
        :return: The hostname
        """
        if isinstance(self.hosts, dict):
            if self.hosts.get("hostnames") is None:
                return None
            return self.hosts["hostnames"]["hostname"]["@name"]

        if self.hosts[i].get("hostnames") is None:
            return None
        return self.hosts[i]["hostnames"]["hostname"]["@name"]

    def get_devices(self) -> list[Device]:
        """
        Get the ip addresses and the hostnames from the scan result
        :return: a dict of the ip addresses and the hostnames
        """
        if isinstance(self.hosts, dict):
            self.hosts = [self.hosts]

        return [
            Device(
                hostname=self.find_hostname(i),
                mac_addr=self.get_address(i, "mac"),
                ip_addr=self.get_address(i, "ipv4"),
                os=None,
                ports=None,
            )
            for i in range(len(self.hosts))
        ]

    def get_hostname(self):
        """
        Retrieves the hostname from the `hosts` dictionary.

        This method attempts to fetch the value of the hostname located within the
        nested structure of the `hosts` dictionary. If any exception occurs during
        the process or if the hostname key is not present, it will return "(Unknown)".

        :return: The hostname if found, otherwise "(Unknown)".
        :rtype: str
        """
        try:
            return self.hosts.get("hostnames", {}).get("hostname", {}).get("@name", "(Unknown)")
        except (AttributeError, TypeError):
            return "(Unknown)"

    def get_ipv4(self):
        """
        Retrieves the IPv4 address from the host's address list.

        This method processes the host's address information to find and
        return any available IPv4 address. If the address data is unavailable
        or an issue occurs during retrieval, appropriate fallback messages
        are returned to indicate the result.

        :return: The IPv4 address as a string if available, "(No IPv4)" if no
            IPv4 address is found, or "(Error)" in case of an exception.
        :rtype: str
        """
        try:
            addresses = self.hosts.get("address", [])
            if isinstance(addresses, dict):
                addresses = [addresses]
            for addr in addresses:
                if addr.get("@addrtype") == "ipv4":
                    return str(addr.get("@addr"))
            return "(No IPv4)"
        except (AttributeError, TypeError):
            return "(Error)"

    def get_ports(self):
        if not isinstance(self.hosts, dict):
            return Port(
                id="(Unknown)",
                protocol="(Unknown)",
                service=Service(name="(Unknown)", os_type="(Unknown)", product="(Unknown)"),
            )
        ports_raw = self.hosts.get("ports", {}).get("port", [])
        if isinstance(ports_raw, dict):
            ports_raw = [ports_raw]
        return [
            Port(
                id=port.get("@portid", ""),
                protocol=port.get("@protocol", ""),
                service=Service(
                    name=port.get("service", {}).get("@name", ""),
                    os_type=port.get("service", {}).get("@ostype", ""),
                    product=port.get("service", {}).get("@product", ""),
                ),
            )
            for port in ports_raw
            if isinstance(port, dict)
        ]

    def get_device(self) -> Device:
        """
        Retrieve the device configuration including hostname, IP address, MAC address,
        operating system details, and associated ports. Uses internal methods to fetch
        each specific detail about the device's configuration. MAC address is left
        unset (None) in this implementation.

        :return: A Device object containing information about the hostname, IP address,
            MAC address, operating system, and ports.
        :rtype: Device
        """
        return Device(
            hostname=self.get_hostname(),
            ip_addr=self.get_ipv4(),
            mac_addr=None,
            os=OperatingSystem(
                name=self.get_os_name_for_host() or "(Unknown)",
                vendor=self.get_os_vendor_to_family()[0],
                family=self.get_os_vendor_to_family()[1],
            ),
            ports=self.get_ports(),
        )
