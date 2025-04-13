from dataclasses import dataclass


@dataclass
class Device:
    """
    Represents a device pulled from the network scan
    """

    hostname: str
    mac_addr: str
    ip_addr: str
