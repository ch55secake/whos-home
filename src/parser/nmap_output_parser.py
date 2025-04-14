from typing import OrderedDict, Any

import xmltodict

from src.data.command_result import CommandResult
from src.data.scan_result import ScanResult
from src.util.logger import Logger


class NmapOutputParser:
    """
    Parse nmap output from xml stdout into json and then into ScanResults
    """

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
        Logger().debug(f"Parsing nmap output from stdout: {self.command_result.stdout} ")
        xml_output: str = self.command_result.stdout
        return xmltodict.parse(xml_output)

    def create_scan_result(self) -> ScanResult:
        """
        Create a scan result object from the parsed xml output
        :return: a scan result object
        """
        Logger().debug("Creating scan result from xml output.... ")
        return ScanResult(run_stats=self.get_runstats(), hosts=self.get_hosts())

    def get_runstats(self) -> OrderedDict[str, Any]:
        """
        Get the run stats from the scan result
        :return: The run stats
        """
        return self.parse()["nmaprun"]["runstats"]

    def get_hosts(self) -> list[OrderedDict[str, Any]]:
        """
        Get the hosts from the scan result
        :return: The hosts
        """
        return self.parse()["nmaprun"]["host"]
