from __future__ import annotations
from dataclasses import dataclass
from subprocess import CompletedProcess


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

    @staticmethod
    def create_command_result(completed_process: CompletedProcess[str], command: str) -> CommandResult:
        return CommandResult(
            command=" ".join(command),
            stdout="" if not completed_process else completed_process.stdout.strip(),
            stderr="" if not completed_process else completed_process.stderr.strip(),
            return_code="" if not completed_process else completed_process.returncode,
            success=("" if not completed_process else completed_process.returncode == 0),
        )
