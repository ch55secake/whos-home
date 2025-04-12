from enum import Enum

from src.data import CommandResult
from src.executor import DefaultExecutor


class NmapExecutor(object):

    def __init__(self, host: str, ranges: str, timeout: float = 60) -> None:
        """
        Executor for nmap commands will provide network scan
        :param host: list of hosts to execute scans on
        :param ranges: ip range to execute scans on
        """
        self.host = host
        self.ranges = ranges
        self.timeout = timeout
        self.executor = DefaultExecutor(timeout=self.timeout)


    def execute_passive_scan(self) -> CommandResult:
        """

        :return:
        """
        command: str = self.build_quiet_slow_scan()
        return self.executor.execute(command)

    def execute_aggressive_scan(self) -> CommandResult:
        """

        :return:
        """
        command: str = self.build_aggressive_privileged_os_scan()
        return self.executor.execute(command)

    def build_quiet_slow_scan(self) -> str:
        """
        Build a quiet slow scan will only scan over common ports with normal timing
        :return: nmap command as a string
        """
        return (f"nmap {AvailableNmapFlags.COMMON_PORTS} "
                f"{AvailableNmapFlags.NORMAL_TIMING} "
                f"{AvailableNmapFlags.XML_OUTPUT_TO_STDOUT} "
                f"{self.host}/{self.ranges}")

    def build_aggressive_privileged_os_scan(self) -> str:
        """
        Build an aggressive privileged scan that will scan and discover OS details quickly, but will only scan over
        common ports
        :return: nmap command as a string
        """
        return (f"sudo nmap {AvailableNmapFlags.COMMON_PORTS} "
                f"{AvailableNmapFlags.AGGRESSIVE_TIMING} "
                f"{AvailableNmapFlags.OS_DETECTION} "
                f"{AvailableNmapFlags.XML_OUTPUT_TO_STDOUT} "
                f"{self.host}/{self.ranges}")




class AvailableNmapFlags(Enum):
    # Need max to add his sweaty little flags

    """
    Available Nmap flags for building commands
    """
    OS_DETECTION = "-O"

    OS_AND_SERVICE_DETECTION = "-A"

    COMMON_PORTS = "-F"

    FULL_PORT_SCAN = "-p-"

    AGGRESSIVE_TIMING = "-T4"

    NORMAL_TIMING = "-T3"

    XML_OUTPUT_TO_STDOUT = "-oX - "
