from dataclasses import dataclass


@dataclass
class CommandResult:
    """
    Result of the command execution.
    """

    command: str
    stdout: str
    stderr: str
    return_code: int
    success: bool
