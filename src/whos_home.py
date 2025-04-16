import os
from typing import Annotated

import typer as t
import xmltodict

from src.data.command_result import CommandResult
from src.data.device import Device
from src.data.scan_result import ScanResult
from src.executor.default_executor import running_as_sudo
from src.executor.nmap_executor import NmapExecutor
from src.output.nmap_output import format_and_output, format_and_output_from_check
from src.parser.nmap_output_parser import NmapHostDiscoveryOutputParser
from src.util.logger import Logger

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
) -> None:
    """
    Discover hosts on the network using nmap
    """
    executor: NmapExecutor = NmapExecutor(host=host, cidr=cidr)
    result_from_host_discovery: CommandResult = execute_host_discovery_based_on_flag(
        only_arp, only_icmp, icmp_and_arp, executor
    )

    if verbose:
        Logger().enable()

    executor: NmapExecutor = NmapExecutor(host=host, cidr=cidr, timeout=timeout)
    if check:
        results_from_check: CommandResult = executor.execute_version_command()
        format_and_output_from_check(command_result=results_from_check)

    if result_from_host_discovery.success:
        parser: NmapHostDiscoveryOutputParser = NmapHostDiscoveryOutputParser(result_from_host_discovery)
        outputted_scan_result: ScanResult = parser.create_scan_result_for_host_discovery()
        outputted_devices: list[Device] = outputted_scan_result.get_devices()
        format_and_output(scan_result=outputted_scan_result, devices=outputted_devices)

        if port_scan:
            Logger().debug("Beginning port scan....")
            with open("ip_list.txt", "w") as file:
                for device in outputted_devices:
                    file.write(f"{device.ip_addr}\n")

            result_from_port_scan: CommandResult = executor.execute_general_port_scan()  # no need for a method in this script as there are no flags. look at line 54

            # someone needs to create a class or some other woke nonsense. I am genuinely too thick to
            # work it out and not break everything. this works for now
            if result_from_port_scan.success:
                print(f'\nPort scan results:')
                # at this point the output dir should be populated with xml files so we need to parse and output them.
                for output_file in os.listdir("output"):
                    host = xmltodict.parse(open(os.path.join("output", output_file), 'r').read()).get('nmaprun',
                                                                                                      {}).get('host',
                                                                                                              {})
                    ip = f"\n{host.get('address', {}).get('@addr', '(Unknown)')}"
                    hostname = host.get('hostnames', {}).get('hostname', {}).get('@name', '(Unknown)')
                    print(f"{ip} {hostname}")

                    open_ports: list | dict = host.get('ports', {}).get('port', [])
                    if not open_ports:
                        print(f"    No open ports found")
                    elif isinstance(open_ports, list):
                        for port in open_ports:
                            # ps, because we are using -sV, we can access port.get('service'), which holds the port name, product and extrainfo.
                            # We can also access @ostype here as well which will give a basic os guess of the target.
                            # I havent implemented this because sometimes, each of these can be None and it would be a bit of a pain to check for each one.
                            print(f"    Port {port.get('@portid')} is open")
                    else:  # for some reason open_ports is a dict when there is only 1 open port found on a host....
                        print(f"    Port {open_ports.get('@portid')} is open")

                # hahahahah i just looked back at what ive written good luck.


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


@app.callback()
def callback() -> None:
    """
    🛰️ Curious about the devices connected to your network?
    """


if __name__ == "__main__":
    t.run(main)
