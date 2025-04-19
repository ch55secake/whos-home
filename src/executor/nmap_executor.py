from __future__ import annotations

import datetime

from rich.progress import Progress, TextColumn, SpinnerColumn

from src.data.command_result import CommandResult
from src.data.executor_callback_events import ExecutorCallbackEvents
from src.executor.default_executor import DefaultExecutor, running_as_sudo
from src.output.typer_output_builder import TyperOutputBuilder
from src.util.logger import Logger
from src.util.nmap_command_builder import NmapCommandBuilder, AvailableNmapFlags


class NmapExecutor:
    """
    Uses DefaultExecutor to execute nmap commands
    """

    def __init__(self, host: str, cidr: str, timeout: float = 120) -> None:
        """
        Executor for nmap commands will provide a network scan
        :param host: list of hosts to execute scans on
        :param cidr: ip range to execute scans on
        :param timeout: timeout of command execution in seconds
        """
        self.host = host
        self.cidr = cidr
        self.timeout = timeout
        self.executor = DefaultExecutor(timeout=self.timeout)
        self.privileged = running_as_sudo()
        self.builder = NmapCommandBuilder(host, cidr, self.privileged)

    def execute_version_command(self) -> CommandResult:
        """
        Executes a version command using the provided builder and executor.

        This method constructs a version command through the `builder`
        object and executes the command to perform host discovery using
        the `executor`. The result of the command execution is returned
        as a `CommandResult` object.

        :return: The result of the version command execution.
        :rtype: CommandResult
        """
        command: str = self.builder.build_version_command()
        return self.executor.execute(command)

    def execute_icmp_host_discovery(self) -> CommandResult:
        """
        Execute a host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_service_scan()
            .enable_exclude_ports()
            .enable_aggressive_timing()
            .enable_icmp_ping()
            .enable_xml_to_stdout()
            .build()
        )
        with Progress(
            TextColumn(" "),
            SpinnerColumn(style="magenta", spinner_name="aesthetic"),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(
                description=TyperOutputBuilder()
                .apply_bold_magenta(" Running: ")
                .apply_bold_cyan(command)
                .apply_bold_magenta(" at: ")
                .apply_bold_cyan(datetime.datetime.now().time().strftime("%H:%M:%S"))
                .apply_bold_magenta(" .......")
                .build(),
                total=None,
            )
            return self.executor.execute(command)

    def execute_arp_host_discovery(self) -> CommandResult:
        """
        Execute an arp host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_service_scan()
            .enable_exclude_ports()
            .enable_aggressive_timing()
            .enable_arp_ping()
            .enable_xml_to_stdout()
            .build()
        )
        return self.executor.execute(command)

    def execute_arp_icmp_host_discovery(self) -> CommandResult:
        """
        Execute an arp and icmp host discovery scan using nmap
        :return: result of command execution
        """
        command: str = (
            self.builder.enable_exclude_ports()
            .enable_aggressive_timing()
            .enable_icmp_ping()
            .enable_arp_ping()
            .enable_xml_to_stdout()
            .build()
        )
        with Progress(
            TextColumn(" "),
            SpinnerColumn(style="magenta", spinner_name="aesthetic"),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(
                description=TyperOutputBuilder()
                .apply_bold_magenta(" Running: ")
                .apply_bold_cyan(command)
                .apply_bold_magenta(" at: ")
                .apply_bold_cyan(datetime.datetime.now().time().strftime("%H:%M:%S"))
                .apply_bold_magenta(" .......")
                .build(),
                total=None,
            )
            return self.executor.execute(command)

    def execute_general_port_scan(self, ips: list[str], events: ExecutorCallbackEvents) -> list[CommandResult]:
        """
        Executes a general port scan on a list of provided IP addresses.

        This function runs a network scan using the `nmap` tool for each IP address
        in the provided list. The scan aims to identify services, operating system
        details, and open ports with aggressive timing and without host discovery.

        The scanning commands are built dynamically using `NmapCommandBuilder`
        and executed in parallel using `async_pooled_execute`. It uses a callback
        function to handle the events.

        :param ips: List of IP addresses to be scanned.
        :type ips: list[str]
        :param events: Callback events for the execution process.
        :type events: ExecutorCallbackEvents
        :return: A list of `CommandResult` objects containing the results of the scan.
        :rtype: list[CommandResult]
        """
        Logger().debug(f"Executing general port scan on {ips}")
        commands: list[str] = list(
            map(
                lambda ip: NmapCommandBuilder(ip, self.cidr)
                .enable_flag(AvailableNmapFlags.COMMON_PORTS)
                .enable_service_scan()
                .enable_aggressive_timing()
                .enable_skip_host_discovery()
                .enable_os_detection()
                .enable_xml_to_stdout()
                .build_without_cidr(),
                ips,
            )
        )

        return self.executor.async_pooled_execute(commands, events)

    def execute_extended_port_scan(self, ips: list[str], events: ExecutorCallbackEvents) -> list[CommandResult]:
        """
        Executes an enhanced port scan on a list of provided IP addresses.
        :param ips:
        :param events:
        :return:
        """
        Logger().debug(f"Executing general port scan on {ips}")

        commands: list[str] = list(
            map(
                lambda ip: NmapCommandBuilder(ip, self.cidr)
                .enable_service_scan()
                .enable_aggressive_timing()
                .enable_skip_host_discovery()
                .enable_os_detection()
                .enable_xml_to_stdout()
                .build_without_cidr(),
                ips,
            )
        )

        return self.executor.async_pooled_execute(commands, events)
