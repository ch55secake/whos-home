from dataclasses import dataclass


@dataclass
class Device:
    """
    Represents a device pulled from the network scan
    """

    hostname: str | None
    ip_addr: str
    mac_addr: str | None
