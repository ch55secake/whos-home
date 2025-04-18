import datetime
import os
import subprocess

import rich
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.data.command_result import CommandResult
from src.output.typer_output_builder import TyperOutputBuilder
from src.util.logger import Logger


class DefaultExecutor:
    """
    Generic executor for any command can be invoked by other more specific executors.
    """

    def __init__(self, timeout: float, warn_about_sudo: bool = True):
        """
        Creates a default command executor to be used by the other executors.
        :param timeout: How long to wait before the subprocess times out.
        """
        self.timeout = timeout
        self.warn_about_sudo = warn_about_sudo

    def execute_host_discovery_command(self, command: str) -> CommandResult:
        """
        Executes a command and returns the result
        :return: command result or none depending on success
        """

        Logger().debug(f"Executing command: {command} with timeout: {self.timeout} and privileged: {running_as_sudo()}")
        if self.warn_about_sudo and not running_as_sudo() and "-PE" in command:
            rich.print(
                TyperOutputBuilder()
                .add_exclamation_mark()
                .apply_bold_red("Warning: ")
                .apply_red()
                .add(
                    " you are not root, this will make nmap fall back to an ICMP ping sweep instead of ICMP and/or ARP."
                    " This means that you may miss hosts on the network and may lose useful information such as the MAC address of the device."
                )
                .clear_formatting()
                .build()
            )

        with Progress(
            # Hack so I can have the spinner more nicely spaced
            TextColumn(" "),
            SpinnerColumn(style="magenta", speed=20),
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
            result = None
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=self.timeout,
                )
            except subprocess.CalledProcessError as e:
                rich.print(
                    TyperOutputBuilder()
                    .apply_bold_red(f" error occurred whilst executing nmap command, error: {e} ")
                    .build()
                )

            Logger().debug("Creating command result.... ")
            return CommandResult(
                command=" ".join(command),
                stdout="" if not result else result.stdout.strip(),
                stderr="" if not result else result.stderr.strip(),
                return_code="" if not result else result.returncode,
                success=("" if not result else result.returncode == 0),
            )

    def execute_port_scan_command(self, command: str) -> CommandResult:
        """ """
        ips = open("ip_list.txt", "r").read().splitlines()
        Logger().debug(f"Running nmap scan on with timeout: {self.timeout} and privileged: {running_as_sudo()}")
        # no sudo warning needed mate
        with Progress(
            # Hack so I can have the spinner more nicely spaced
            TextColumn(" "),
            SpinnerColumn(style="magenta", speed=20),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        ) as progress:
            progress.add_task(
                description=f"[bold magenta] Running [bold cyan]{command}[/bold cyan] at: "
                f"[bold cyan]{datetime.datetime.now().time().strftime("%H:%M:%S")}[/bold cyan] "
                f".......[/bold magenta]",
                total=None,
            )
            result = None
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=self.timeout,
                )
            except subprocess.CalledProcessError as e:
                rich.print(f"[bold red] error occurred whilst executing nmap command, error: {e} [/bold red]")

            return CommandResult(
                command=command,
                stdout="" if not result else result.stdout.strip(),
                stderr="" if not result else result.stderr.strip(),
                return_code="" if not result else result.returncode,
                success=("" if not result else result.returncode == 0),
            )


def running_as_sudo() -> bool:
    """
    Detect if the user is running as sudo
    :return: bool based on if the user is sudo
    """
    return os.getuid() == 0
