from dataclasses import dataclass
from typing import OrderedDict, Any


@dataclass
class ScanResult:
    """
    Class to represent the result of a scan.
    """

    run_stats: OrderedDict[str, Any]
    hosts: list[dict]

    def get_ip_address(self):
        """
        Get the ip address from the scan result
        :return: The ip address
        """
        return self.hosts[0]["address"].get("@addr")

    def get_mac_address(self):
        """
        Get the mac address from the scan result
        :return: The mac address
        """
        return self.hosts[0]["address"].get("@mac")

    def get_hostname(self):
        """
        Get the hostname from the scan result
        :return: The hostname
        """
        return self.hosts[0]["hostnames"]["hostname"].get("@name")
