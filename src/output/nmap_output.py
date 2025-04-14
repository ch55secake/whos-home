import rich

from src.data.device import Device
from src.data.scan_result import ScanResult


def format_and_output(scan_result: ScanResult, devices: list[Device]) -> None:
    """
    Neatly outputs the devices it finds
    :param scan_result: scan_result from nmap input
    :param devices: set of devices to output
    :return: nothing, will just print
    """
    for device in devices:
        rich.print(get_ip_and_mac_message(device))
    rich.print("\n" + get_unique_devices_message(devices) + "\n" + get_host_totals_message(scan_result))


def check_hostname_is_none(hostname: str | None) -> str:
    """
    Check if the provided hostname is None and return a default message if it is
    :param hostname: the hostname to check
    :return: the str message to be printed
    """
    if isinstance(hostname, str):
        return hostname
    return "(Unknown)"


def build_ip_message(device: Device) -> str:
    device.ip_addr += " " * (3 - len(device.ip_addr.split(".")[3]))
    return f" 🛰️ [bold magenta] Found ip address: [/bold magenta][bold cyan]{device.ip_addr}[/bold cyan] "


def build_mac_addr_message(device: Device) -> str | None:
    """
    For a mac address there is a chance it's not present in the device, depending on if the user runs the command with
    sudo or not hence the need for the check
    :param device: to pull the mac address from
    :return: string containing the mac address message
    """
    if device.mac_addr is not None:
        return f"[bold magenta]and mac address: [/bold magenta][bold cyan]{device.mac_addr}[/bold cyan] "


def get_ip_and_mac_message(device: Device) -> str:
    """
    Get the message that contains the ip address, mac address and host name
    :param device: the device being iterated over
    :return: the str message to be printed
    """
    # Warning: The spacing is extremely finicky. Change at your own risk.
    mac_addr_message: str = build_mac_addr_message(device)
    if mac_addr_message:
        return (
            build_ip_message(device) + mac_addr_message + f"[bold magenta]for hostname:[/bold magenta] "
            f"[bold cyan]{check_hostname_is_none(device.hostname)}[/bold cyan]"
        )
    return (
        build_ip_message(device) + f"[bold magenta]for hostname:[/bold magenta]"
        f"[bold cyan] {check_hostname_is_none(device.hostname)}[/bold cyan]"
    )


def get_number_of_unique_devices(devices: list[Device]) -> int:
    """
    Get the number of unique devices based on the hostname
    :param devices: all devices passed in from the list
    :return: number of unique devices in the list
    """
    unique_hostnames: set = {device.hostname for device in devices if device.hostname is not None}
    return len(unique_hostnames)


def get_unique_devices_message(devices: list[Device]) -> str:
    """
    Get the unique devices message to be printed to the user
    :param devices: list of devices to check how many are unique
    :return: the str message to be printed
    """
    return (
        f"[bold magenta] ✔️ Scan suggests that you have: [/bold magenta]"
        f"[bold cyan]{get_number_of_unique_devices(devices)}[/bold cyan] "
        f"[bold magenta]unique devices on the network. [/bold magenta]"
    )


def get_host_totals_message(scan_result: ScanResult) -> str:
    """
    Provide extra information about the number of hosts that were scanned
    :param scan_result: scan_result that has the run stats on it
    :return: the str message to be printed
    """
    hosts_up: int = scan_result.get_hosts_up_from_runstats() - 1
    total_hosts_scanned: str = scan_result.get_total_hosts_from_runstats()
    return (
        f"[bold magenta] ✔️ It also found [bold cyan]{hosts_up}[/bold cyan] hosts up after scanning a total of "
        f"[bold cyan]{total_hosts_scanned}[/bold cyan] hosts[/bold magenta]"
    )
