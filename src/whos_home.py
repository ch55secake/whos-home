from functools import partial
from typing import Annotated

import schedule as scheduler
import typer as t

from src.data.command_result import CommandResult
from src.data.nmapdevice import NmapDevice
from src.data.executor_callback_events import ExecutorCallbackEvents
from src.data.scan_result import ScanResult
from src.executor.default_executor import running_as_sudo
from src.executor.nmap_executor import NmapExecutor
from src.output.nmap_output import format_and_output, format_and_output_from_check
from src.parser.nmap_output_parser import NmapOutputParser
from src.util.logger import Logger
from src.util.scheduler import Scheduler

app: t.Typer = t.Typer()


@app.command(
    help="Scan a provided host to find the devices that are currently on the host that you provided, "
    "will execute either a passive or aggressive scan depending on the option provided. You are also "
    "able to provide a given CIDR that you want to scan across. The CIDR will default to 24.",
    short_help="Scan for details about your network",
)
def main(
    host: Annotated[str, t.Argument(help="The host that you want to scan against.")],
    cidr: Annotated[str, t.Option(help="The CIDR of the host that you want to scan against.")] = "24",
    schedule: Annotated[
        str, t.Option(help="Run scans on a schedule of any of these values: 5m, 15m, 30m, 45m, 1h")
    ] = "",
    host_range: Annotated[str, t.Option(help="Run scans against a range of IPs.")] = "",
    only_icmp: Annotated[bool, t.Option(help="Run scans with just an ICMP packet")] = not running_as_sudo(),
    only_arp: Annotated[bool, t.Option(help="Run scans with just an ARP packet")] = False,
    icmp_and_arp: Annotated[bool, t.Option(help="Run scans with just an ICMP and ARP packet")] = running_as_sudo(),
    port_scan: Annotated[bool, t.Option(help="Run a port scan against discovered hosts")] = False,
    verbose: Annotated[bool, t.Option(help="Verbose output when invoking nmap scans")] = False,
    check: Annotated[bool, t.Option(help="Check if nmap installation is working")] = False,
    timeout: Annotated[int, t.Option(help="Control the duration of the command execution")] = 60,
    extended_port_scan: Annotated[bool, t.Option(help="Scan more ports (1000) than the default port scan.")] = False,
    full_port_scan: Annotated[bool, t.Option(help="Scan all ports.")] = False,
) -> None:
    """
    Discover hosts on the network using nmap
    """
    hosts = parse_hosts(host)
    for host in hosts:
        executor: NmapExecutor = NmapExecutor(host=host, cidr=cidr, timeout=timeout)
        result_from_host_discovery: CommandResult = execute_host_discovery_based_on_flag(
            only_arp, only_icmp, icmp_and_arp, executor
        )

        if schedule != "" or None:
            Scheduler().schedule_task(
                schedule_value=schedule,
                main_fn=main,
                host=host,
                cidr=cidr,
                timeout=timeout,
                verbose=verbose,
                check=check,
                port_scan=port_scan,
                extended_port_scan=extended_port_scan,
            )

        if verbose:
            Logger().enable()

        if check:
            results_from_check: CommandResult = executor.execute_version_command()
            format_and_output_from_check(command_result=results_from_check)

        if result_from_host_discovery.success:
            parser: NmapOutputParser = NmapOutputParser(result_from_host_discovery)
            outputted_scan_result: ScanResult = parser.create_scan_result()
            outputted_devices: list[NmapDevice] = outputted_scan_result.get_devices()
            format_and_output(scan_result=outputted_scan_result, devices=outputted_devices)

            if port_scan:
                perform_port_scan("general", outputted_devices, executor)

            if extended_port_scan:
                perform_port_scan("extended", outputted_devices, executor)

            if full_port_scan:
                perform_port_scan("full", outputted_devices, executor)


def perform_port_scan(scan_type: str, devices: list, executor):
    """
    Performs a port scan on the devices using the specified scan type.
    :param scan_type: The type of scan to perform. Can be "general", "extended", or "full".
    :param devices: The devices to scan.
    :param executor: The executor to use for the scan.
    :return: None
    """
    Logger().debug("Beginning port scan....")
    ips: list[str] = [device.ip_addr for device in devices]
    callbacks = ExecutorCallbackEvents(
        ExecutorCallbackEvents.pre_execution_callback,
        ExecutorCallbackEvents.post_execution_callback,
    )

    scan_methods = {
        "general": executor.execute_general_port_scan,
        "extended": executor.execute_extended_port_scan,
        "full": executor.execute_full_port_scan,
    }

    scan_method = scan_methods.get(scan_type)
    if scan_method:
        scan_method(ips, callbacks)


def execute_host_discovery_based_on_flag(
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
        Logger().debug("Running nmap with both arp and icmp...")
        return executor.execute_arp_icmp_host_discovery()
    Logger().debug(f"Running nmap with only {"arp" if only_arp else "icmp"}...")
    return executor.execute_arp_host_discovery() if only_arp else executor.execute_icmp_host_discovery()


def parse_hosts(host: str) -> list[str]:
    """
    Check the host given in the command line and return a list of hosts. If only one host is given, returns a list of one host. If there were multiple hosts, it will return a list of those hosts.
    :param host: The host that you want to scan against.
    :return: A list of hosts.
    """
    return host.split(" ") if " " in host else [host]


@app.callback()
def callback() -> None:
    """
    🛰️ Curious about the devices connected to your network?
    """


if __name__ == "__main__":
    t.run(main)
