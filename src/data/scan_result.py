from __future__ import annotations

from dataclasses import dataclass
from typing import OrderedDict, Any

from src.data.device import Device


@dataclass
class ScanResult:
    """
    Class to represent the result of a scan.
    """

    run_stats: OrderedDict[str, Any]
    hosts: list[dict]

    def get_hosts_up_from_runstats(self) -> str:
        """
        Pull host info of the run stats
        :return: number of hosts up as string
        """
        return self.run_stats["hosts"]["@up"]

    def get_total_hosts_from_runstats(self) -> str:
        """
        Pull total number of hosts from the run stats
        :return: total number of hosts up as a string
        """
        return self.run_stats["hosts"]["@total"]

    def get_address(self, i, address_type: str) -> str:
        """
        Get the address from the scan result based on type
        :return: The address
        """
        addresses = self.hosts[i]["address"]
        if isinstance(addresses, dict):
            addresses = [addresses]

        for address in addresses:
            if address["@addrtype"] == address_type:
                return address["@addr"]

    def get_hostname(self, i: int) -> str:
        """
        Get the hostname from the scan result
        :return: The hostname
        """
        return self.hosts[i]["hostnames"]["hostname"]["@name"]

    def get_devices(self) -> list[Device]:
        """
        Get the ip addresses and the hostnames from the scan result
        :return: a dict of the ip addresses and the hostnames
        """
        return [
            Device(
                hostname=self.get_hostname(i), mac_addr=self.get_address(i, "mac"), ip_addr=self.get_address(i, "ipv4")
            )
            for i in range(len(self.hosts) - 1)
        ]
