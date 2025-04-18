import re

from rich import print

from src.data.command_result import CommandResult
from src.data.device import Device
from src.data.scan_result import ScanResult
from src.output.typer_output_builder import TyperOutputBuilder
from src.util.logger import Logger


def format_and_output_from_check(command_result: CommandResult) -> None:
    """
    Check nmap version, and if its person return a
    :param command_result: result of command execution
    :return: nothing just output message containing nmap version
    """
    Logger().debug("Checking for valid nmap installation.... ")
    nmap_version_pattern: str = r"Nmap version \d+\.\d+"
    version_found: re.Match[str] = re.search(nmap_version_pattern, command_result.stdout)

    if version_found:
        version = version_found.group().replace("Nmap version", "").strip()
        output_message: str = (
            TyperOutputBuilder()
            .add_check_mark()
            .apply_bold_magenta(f" Found nmap version: ")
            .apply_bold_cyan(f"{version}")
            .build()
        )
        print(output_message + "\n")
    else:
        print(
            TyperOutputBuilder()
            .apply_bold_red()
            .add_exclamation_mark()
            .add(" ERROR: no valid nmap version found, please check your current installation... ")
            .build()
        )


def format_and_output(scan_result: ScanResult, devices: list[Device]) -> None:
    """
    Neatly outputs the devices it finds
    :param scan_result: scan_result from a nmap input
    :param devices: set of devices to output
    :return: nothing, will just print
    """
    Logger().debug("Looping through devices to output.... ")
    print(get_result_summary_message())
    for device in devices:
        print(get_ip_and_mac_message(device))
    print(
        "\n"
        + get_unique_devices_message(devices)
        + "\n"
        + get_host_totals_message(scan_result)
        + "\n"
        + build_post_scan_message()
    )


def format_and_output_from_port_scan(scan_result: ScanResult) -> None:
    """
    Format and output the port scan results; this will also include any OS information found
    :param scan_result: result from the scan
    :return: nothing only outputs to the user
    """
    Logger().debug("Outputting port scan results.... ")
    print("\n".join(build_port_message(scan_result)) + "\n" + build_os_info_message(scan_result))


def get_result_summary_message() -> str:
    """
    Output the summary message before printing any results from the scan
    :return: nothing, only outputs to the user
    """
    return TyperOutputBuilder().add_satellite().apply_bold_magenta(message=" Hosts found on your network: ").build()


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
    """
    Build the ip message to be printed to the user
    :param device: found from the scan
    :return: string message to be printed to the user
    """
    formatted_ip_addr = device.ip_addr + " " * (3 - len(device.ip_addr.split(".")[3]))
    return (
        TyperOutputBuilder()
        .apply_bold_magenta()
        .add_square()
        .clear_formatting()
        .apply_bold_magenta(message=" Found ip address: ")
        .apply_bold_cyan(message=f"{formatted_ip_addr} ")
        .build()
    )


def build_post_scan_message() -> str:
    """
    Build the post-scan message to be printed to the user
    :return: str message to be printed to the user
    """
    return TyperOutputBuilder().apply_bold_magenta(message=" [~] Scan complete!").build()


def build_mac_addr_message(device: Device) -> str | None:
    """
    For a mac address there is a chance it's not present in the device, depending on if the user runs the command with
    sudo or not, hence the need for the check
    :param device: to pull the mac address from
    :return: string containing the mac address message
    """
    if device.mac_addr is not None:
        return (
            TyperOutputBuilder()
            .apply_bold_magenta(message="add mac address: ")
            .apply_bold_cyan(message=f"{device.mac_addr} ")
            .build()
        )
    return None


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
            TyperOutputBuilder()
            .add(build_ip_message(device))
            .add(mac_addr_message)
            .apply_bold_magenta(message="for hostname: ")
            .apply_bold_cyan(message=check_hostname_is_none(device.hostname))
            .build()
        )
    return (
        TyperOutputBuilder()
        .add(build_ip_message(device))
        .apply_bold_magenta(message="for hostname: ")
        .apply_bold_cyan(message=check_hostname_is_none(device.hostname))
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
        .add_check_mark()
        .apply_bold_magenta(message="Scan suggests that you have: ")
        .apply_bold_cyan(message=get_number_of_unique_devices(devices))
        .apply_bold_magenta(message=" unique devices on the network. ")
        .build()
    )


def get_host_totals_message(scan_result: ScanResult) -> str:
    """
    Provide extra information about the number of hosts that were scanned
    :param scan_result: scan_result that has the run stats on it
    :return: the str message to be printed
    """
    hosts_up: int = scan_result.get_hosts_up_from_runstats()
    total_hosts_scanned: str = scan_result.get_total_hosts_from_runstats()
    return (
        TyperOutputBuilder()
        .add_check_mark()
        .apply_bold_magenta(message="It also found ")
        .apply_bold_cyan(message=hosts_up)
        .apply_bold_magenta(message=" hosts up after scanning a total of ")
        .apply_bold_cyan(message=total_hosts_scanned)
        .apply_bold_magenta(message=" hosts")
        .build()
    ) + "\n"


def build_port_message(scan_result: ScanResult) -> list[str]:
    """
    Build the port message to be printed to the user requires iteration as there is sometimes a list of ports
    :param scan_result: scan_result to get the device from and the ports from
    :return: a list of str messages to be printed to the user
    """
    device_from_port_scan: Device = scan_result.get_device()
    return [
        TyperOutputBuilder()
        .apply_bold_magenta()
        .add_square()
        .add(" Found ports: ")
        .clear_formatting()
        .apply_bold_cyan(message="{:<10}".format(f"{port.id}/{port.protocol}"))
        .apply_bold_magenta(message=" for host: ")
        .apply_bold_cyan(
            message=f"{device_from_port_scan.ip_addr}({check_hostname_is_none(device_from_port_scan.hostname)})"
        )
        .build()
        for port in device_from_port_scan.ports
    ]


def build_os_info_message(scan_result: ScanResult) -> str:
    """
    Build the os info message to be printed from the port scan results
    :param scan_result: scan_result to get the device from and the os info from
    :return: a message to be printed to the user
    """
    device_from_port_scan: Device = scan_result.get_device()
    return (
        TyperOutputBuilder()
        .apply_bold_magenta()
        .add_square()
        .add(" Found OS information: ")
        .clear_formatting()
        .apply_bold_cyan(
            message=f"{device_from_port_scan.os.name}/{device_from_port_scan.os.vendor}/{device_from_port_scan.os.family}"
        )
        .apply_bold_magenta(message=" for host: ")
        .apply_bold_cyan(
            message="{:<10}".format(
                f"{device_from_port_scan.ip_addr}({check_hostname_is_none(device_from_port_scan.hostname)})"
            )
        )
        .build()
    )
