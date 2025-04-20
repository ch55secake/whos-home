import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
from typing import Iterator

import rich
from rich.progress import TaskID

from src.data.command_result import CommandResult
from src.data.executor_callback_events import ExecutorCallbackEvents
from src.output.typer_output_builder import TyperOutputBuilder
from src.util.logger import Logger
from src.util.progress_service import ProgressService


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
        self.timeout_warning = False

    def execute(self, command: str) -> CommandResult:
        """
        Executes a command and returns the result
        :return: command result or none depending on success
        """
        self.output_sudo_warning(command)
        result = None
        try:
            Logger().debug(
                f"Executing command: {command} with timeout: {self.timeout} and privileged: {running_as_sudo()}"
            )
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
        except (TimeoutError, subprocess.TimeoutExpired):
            if not self.timeout_warning:
                rich.print(
                    TyperOutputBuilder()
                    .add_exclamation_mark()
                    .apply_bold_red(
                        f" Timeout occurred whilst executing command! Consider raising the timeout value with --timeout flag. "
                    )
                    .build()
                )
                self.timeout_warning = True

        Logger().debug("Creating command result.... ")
        return CommandResult.create_command_result(result, command)

    def output_sudo_warning(self, command):
        if self.warn_about_sudo and not running_as_sudo() and "-PE" in command:
            rich.print(
                TyperOutputBuilder()
                .add_exclamation_mark()
                .apply_bold_red("Warning: ")
                .apply_red()
                .add(
                    " you are not root, this will make nmap fall back to an ICMP ping sweep instead of ICMP and/or ARP."
                    " This means that you may miss hosts on the network and may lose useful information "
                    " such as the MAC address of the device."
                )
                .clear_formatting()
                .build()
            )

    def async_pooled_execute(self, commands: list[str], events: ExecutorCallbackEvents) -> list[CommandResult]:
        """
        Executes a list of commands asynchronously and in parallel using a
        thread pool executor, ensuring that each command is executed in
        conjugation with the provided event callbacks.

        This method helps to efficiently execute multiple commands concurrently
        and return their results in a pooled manner. It also outputs any sudo
        warning message for the first command in the list.

        :param commands: A list of commands that need to be executed asynchronously.
        :param events: Events used as callbacks related to execution, implementing
            relevant handling during processing.
        :return: A list of results corresponding to the execution of each command.
        :rtype: list[CommandResult]
        """
        self.output_sudo_warning(commands[0])
        with ProgressService().progress:
            with ThreadPoolExecutor(max_workers=20) as executor:
                results: Iterator[CommandResult] = executor.map(
                    lambda args: self.async_execute(*args), [(command, events) for command in commands]
                )
            return list(results)

    def async_execute(self, command: str, events: ExecutorCallbackEvents) -> CommandResult:
        """
        Executes a command asynchronously while handling pre-execution callbacks
        and providing the execution result. This function delegates execution to
        a synchronous execution method and utilizes provided callbacks to perform
        additional actions before execution is completed.

        :param command: The command string to be executed. This should be a valid
            shell command or relevant executable instruction.
        :type command: str
        :param events: An instance containing callbacks for execution events.
            Particularly, `pre_execution` is invoked before command execution to handle
            required pre-execution logic.
        :type events: ExecutorCallbackEvents
        :return: A `CommandResult` instance containing execution data such as success
            status, output, and error messages resulting from the executed command.
        :rtype: CommandResult
        """
        task_id: TaskID = events.pre_execution(command)
        command_result: CommandResult = self.execute(command)
        events.post_execution(command_result, task_id)
        return command_result


def running_as_sudo() -> bool:
    """
    Detect if the user is running as sudo
    :return: bool based on if the user is sudo
    """
    return os.getuid() == 0
