import datetime
import os
import subprocess

import rich
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.data.command_result import CommandResult


class DefaultExecutor:
    """
    Generic executor for any command, can be invoked by other more specific executors.
    """

    def __init__(self, timeout: float, warn_about_sudo: bool = True):
        """
        Creates a default command executor to be used by the other executors.
        :param timeout: how long to wait before the subprocess times out.
        """
        self.timeout = timeout
        self.warn_about_sudo = warn_about_sudo

    def execute(self, command: str) -> CommandResult:
        """
        Executes a command and returns the result
        :return: command result or none depending on success
        """

        if self.warn_about_sudo and not running_as_sudo():
            rich.print(
                "❗️[bold red] Warning:[/bold red][red] you are not root, this will make nmap fall back to a TCP scan "
                "instead of ARP or ICMP. This also means that you will lose information such as the MAC address of "
                "the device.[red] "
            )

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
                command=" ".join(command),
                stdout="" if not result else result.stdout.strip(),
                stderr="" if not result else result.stderr.strip(),
                return_code="" if not result else result.returncode,
                success=("" if not result else result.returncode == 0),
            )


def running_as_sudo() -> bool:
    """
    Detect if the user is running as sudo
    :return: bool based on if user is sudo
    """
    return os.getuid() == 0
