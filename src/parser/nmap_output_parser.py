from src.data import CommandResult


class NmapOutputParser:

    def __init__(self, command_result: CommandResult) -> None:
        """

        :param command_result:
        """
        self.command_result = command_result
