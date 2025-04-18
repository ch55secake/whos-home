from dataclasses import dataclass


@dataclass
class OperatingSystem:
    """
    Represents the operating system of a device pulled from a port scan
    """

    name: str
    vendor: str
    family: str


@dataclass
class Service:
    """
    Represents the service on a port pulled from a port scan
    """

    name: str
    product: str
    os_type: str


@dataclass
class Port:
    """
    Represents a port pulled from a port scan
    """

    id: str
    protocol: str
    service: Service


@dataclass
class Device:
    """
    Represents a device pulled from the network scan
    """

    hostname: str | None
    ip_addr: str
    mac_addr: str | None
    os: OperatingSystem | None
    ports: list[Port] | None
