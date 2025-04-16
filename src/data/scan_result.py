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
    hosts: list[dict] | dict

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

    def get_hostname(self, i: int) -> Any | None:
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
        return [
            Device(
                hostname=self.get_hostname(i), mac_addr=self.get_address(i, "mac"), ip_addr=self.get_address(i, "ipv4")
            )
            for i in range(len(self.hosts) - 1)
        ]
