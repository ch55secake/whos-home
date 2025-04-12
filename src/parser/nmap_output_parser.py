from typing import OrderedDict, Any

import xmltodict

from src.data.command_result import CommandResult


class NmapOutputParser:

    def __init__(self, command_result: CommandResult) -> None:
        """
        Takes a given command result and pulls the xml from the stdout and converts it to json
        :param command_result:
        """
        self.command_result = command_result


    def parse(self) -> OrderedDict[str, Any]:
        """
        Parse the xml output and return an OrderedDict
        :return: an ordered dict from the xml output
        """
        xml_output: str = self.command_result.stdout
        return xmltodict.parse(xml_output)
