from typing import Annotated

import typer as t

from src.data.command_result import CommandResult
from src.data.device import Device
from src.executor.nmap_executor import NmapExecutor
from src.output.nmap_output import format_and_output
from src.parser.nmap_output_parser import NmapOutputParser

app: t.Typer = t.Typer()


@app.command(
    help="Scan a provided host to find the devices that are currently on the host that you provided, "
    "will execute either a passive or aggressive scan depending on the option provided. You are also "
    "able to provide a given CIDR that you want to scan across. The CIDR will default to 24.",
    short_help="Scan for details about your network",
)
def now(
    host: Annotated[str, t.Argument(help="The host that you want to scan against.")],
    cidr: Annotated[str, t.Option(help="The CIDR of the host that you want to scan against.")] = "24",
    schedule: Annotated[
        str, t.Option(help="Run scans on a schedule of any of these values: 5m, 15m, 30m, 45m, 1h")
    ] = "",
    host_range: Annotated[str, t.Option(help="Run scans against a range of IPs.")] = "",
    only_icmp: Annotated[bool, t.Option(help="Run scans with just an ICMP packet")] = False,
    only_arp: Annotated[bool, t.Option(help="Run scans with just an ARP packet")] = False,
    icmp_and_arp: Annotated[bool, t.Option(help="Run scans with just an ICMP and ARP packet")] = True,
):
    """
    Discover hosts on the network using nmap
    """
    executor: NmapExecutor = NmapExecutor(host=host, cidr=cidr)
    result_from_scan: CommandResult = execute_scan_based_on_flag(only_arp, only_icmp, icmp_and_arp, executor)

    if result_from_scan.success:
        parser: NmapOutputParser = NmapOutputParser(result_from_scan)
        outputted_devices: list[Device] = parser.create_scan_result().get_devices()
        format_and_output(outputted_devices)


def execute_scan_based_on_flag(
    only_arp: bool, only_icmp: bool, icmp_and_arp: bool, executor: NmapExecutor
) -> CommandResult:
    """
    Decides which executor to invoke and executes the scan with that configuration
    :param only_arp: will run only ARP scans
    :param executor: executor to invoke
    :param only_icmp: will only run ICMP scans
    :param icmp_and_arp: will run both ICMP and ARP scans
    :return: the command result after command execution
    """
    if only_arp and only_icmp or icmp_and_arp:
        return executor.execute_arp_icmp_host_discovery()
    return executor.execute_arp_host_discovery() if only_arp else executor.execute_icmp_host_discovery()


@app.callback()
def callback() -> None:
    """
    🛰️ Curious about the devices connected to your network?
    """


def main() -> None:
    """
    Entrypoint hack for poetry builds
    :return: nothing starts the app
    """
    app()


if __name__ == "__main__":
    main()
