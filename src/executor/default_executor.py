import datetime
import subprocess
import time

import rich
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.data.command_result import CommandResult

class DefaultExecutor:

    def __init__(self, timeout: float):
        """
        Creates a default command executor to be used by the other executors.
        :param timeout:
        """
        self.timeout = timeout

    def execute(self, command: str) -> CommandResult | None:
        """
        Executes a command and returns the result
        :return: command result or none depending on success
        """
        with Progress(
                SpinnerColumn(style="magenta"),
                TextColumn("[progress.description]{task.description}"),
                transient=True,
        )as progress:
            progress.add_task(description=f"[bold magenta] Running [bold cyan]{command}[/bold cyan] at: [bold cyan]{datetime.datetime.now().time().strftime("%H:%M:%S")}[/bold cyan] .......[/bold magenta]", total=None)
            try:
                result: subprocess.CompletedProcess[str] = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    check=True,
                    timeout=self.timeout,
                )
                return CommandResult(
                    command=" ".join(command),
                    stdout=result.stdout.strip(),
                    stderr=result.stderr.strip(),
                    return_code=result.returncode,
                    success=(result.returncode == 0)
                )
            except subprocess.CalledProcessError as e:
                rich.print("[bold red] error occurred whilst executing nmap command, error: {} [/bold red]".format(e))

    def execute_with_xargs(self, command: str) -> CommandResult:
        """

        :param command:
        :return:
        """
        pass
