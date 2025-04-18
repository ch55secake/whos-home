import datetime
from dataclasses import dataclass
from typing import Callable

from rich.progress import TaskID

from src.data.command_result import CommandResult
from src.data.scan_result import ScanResult
from src.output.nmap_output import format_and_output_from_port_scan
from src.output.typer_output_builder import TyperOutputBuilder
from src.parser.nmap_output_parser import NmapOutputParser
from src.util.logger import Logger
from src.util.progress_service import ProgressService


@dataclass
class ExecutorCallbackEvents:
    """
    Handles callback events during the execution process.

    The `ExecutorCallbackEvents` class is a data structure that allows registration
    of callback functions to be executed before and after a command execution.
    This can be used to perform custom logic at specific execution stages.

    :ivar pre_execution: A callable executed with a string argument before the execution
        of a command. It can be used for pre-processing or logging purposes.
    :type pre_execution: Callable[[str], None]
    :ivar post_execution: A callable executed with a `CommandResult` argument after the
        execution of a command. It can be used for processing the result or post-execution
        logging.
    :type post_execution: Callable[[CommandResult], None]
    """

    pre_execution: Callable[[str], TaskID]
    post_execution: Callable[[CommandResult, TaskID], None]

    @staticmethod
    def pre_execution_callback(command: str) -> TaskID:
        task: TaskID = ProgressService().progress.add_task(
            description=TyperOutputBuilder()
            .apply_bold_magenta(" Running: ")
            .apply_bold_cyan(command)
            .apply_bold_magenta(" at: ")
            .apply_bold_cyan(datetime.datetime.now().time().strftime("%H:%M:%S"))
            .apply_bold_magenta(" .......")
            .build()
        )

        Logger().debug(f"Creating progress with task_id: {task}")
        return task

    @staticmethod
    def post_execution_callback(command_result: CommandResult, task_id: TaskID) -> None:
        Logger().debug("Completing progress task....")
        ProgressService().progress.update(task_id, completed=True, visible=False)

        if command_result.success:
            parser: NmapOutputParser = NmapOutputParser(command_result)
            outputted_scan_result: ScanResult = parser.create_scan_result()
            format_and_output_from_port_scan(outputted_scan_result)
