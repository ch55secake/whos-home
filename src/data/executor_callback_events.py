from dataclasses import dataclass
from typing import Callable

from rich.progress import TaskID

from src.data.command_result import CommandResult


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
