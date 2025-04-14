import datetime
import logging

import rich

from output.typer_output_builder import TyperOutputBuilder
from src.data.device import Device
from src.data.scan_result import ScanResult
from src.util.logger import Logger


def format_and_output(scan_result: ScanResult, devices: list[Device]) -> None:
    """
    Neatly outputs the devices it finds
    :param scan_result: scan_result from nmap input
    :param devices: set of devices to output
    :return: nothing, will just print
    """
    Logger().debug("Looping through devices to output.... ")
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
    formatted_ip_addr = device.ip_addr + " " * (3 - len(device.ip_addr.split(".")[3]))
    return (
        TyperOutputBuilder()
        .add(" 🛰️ ")
        .apply_bold_magenta()
        .add(" Found ip address: ")
        .clear_formatting()
        .apply_bold_cyan()
        .add(f"{formatted_ip_addr} ")
        .build()
    )


def build_mac_addr_message(device: Device) -> str | None:
    """
    For a mac address there is a chance it's not present in the device, depending on if the user runs the command with
    sudo or not hence the need for the check
    :param device: to pull the mac address from
    :return: string containing the mac address message
    """
    if device.mac_addr is not None:
        return (
            TyperOutputBuilder()
            .apply_bold_magenta()
            .add("add mac address: ")
            .clear_formatting()
            .apply_bold_cyan()
            .add(f"{device.mac_addr} ")
            .build()
        )


def get_ip_and_mac_message(device: Device) -> str:
    """
    Get the message that contains the ip address, mac address and host name
    :param device: the device being iterated over
    :return: the str message to be printed
    """
    # Warning: The spacing is extremely finicky. Change at your own risk.
    mac_addr_message: str = build_mac_addr_message(device)
    if mac_addr_message:
        # return (
        #     build_ip_message(device) + mac_addr_message + f"[bold magenta]for hostname:[/bold magenta] "
        #     f"[bold cyan]{check_hostname_is_none(device.hostname)}[/bold cyan]"
        # )
        return (
            TyperOutputBuilder()
            .add(build_ip_message(device))
            .add(mac_addr_message)
            .apply_bold_magenta()
            .add("for hostname: ")
            .clear_formatting()
            .apply_bold_cyan()
            .add(check_hostname_is_none(device.hostname))
            .build()
        )
    return (
        TyperOutputBuilder()
        .add(build_ip_message(device))
        .apply_bold_magenta()
        .add("for hostname:")
        .clear_formatting()
        .apply_bold_cyan()
        .add(check_hostname_is_none(device.hostname))
        .build()
    )


def get_number_of_unique_devices(devices: list[Device]) -> int:
    """
    Get the number of unique devices based on the ip addresses
    :param devices: all devices passed in from the list
    :return: number of unique devices in the list
    """
    unique_devices: set[str] = {device.ip_addr for device in devices if device.ip_addr is not None}
    return len(unique_devices)


def get_unique_devices_message(devices: list[Device]) -> str:
    """
    Get the unique devices message to be printed to the user
    :param devices: list of devices to check how many are unique
    :return: the str message to be printed
    """
    return (
        TyperOutputBuilder()
        .apply_bold_magenta()
        .add(" ✔️ Scan suggests that you have: ")
        .clear_formatting()
        .apply_bold_cyan()
        .add(get_number_of_unique_devices(devices))
        .clear_formatting()
        .apply_bold_magenta()
        .add(" unique devices on the network. ")
        .build()
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
        TyperOutputBuilder()
        .apply_bold_magenta()
        .add(" ✔️ It also found ")
        .clear_formatting()
        .apply_bold_cyan()
        .add(hosts_up)
        .clear_formatting()
        .apply_bold_magenta()
        .add(" hosts up after scanning a total of ")
        .clear_formatting()
        .apply_bold_cyan()
        .add(total_hosts_scanned)
        .clear_formatting()
        .apply_bold_magenta()
        .add(" hosts")
        .build()
    )
