import time
from functools import partial

import rich
import schedule
from rich.progress import Progress, BarColumn, TimeRemainingColumn, DownloadColumn, TaskProgressColumn

from src.output.typer_output_builder import TyperOutputBuilder


class Scheduler:
    """
    Singleton class for scheduling tasks
    """

    _instance = None
    _initialized = False

    _available_schedules = ["1m", "5m", "15m", "30m", "45m", "1h"]

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not Scheduler._initialized:
            Scheduler._initialized = True

    def schedule_task(
        self, schedule_value: str, main_fn, *, host, cidr, port_scan, verbose, check, timeout, extended_port_scan
    ):
        """
        Schedules a task to execute a given function at a specified interval, defined
        by the schedule value. The function is executed with the provided parameters
        using Python's `schedule` library. The scheduling continues indefinitely,
        and a visual timer bar is displayed during idle intervals.

        :param schedule_value: The scheduling interval, specified as a string
            (e.g., "1s" for 1 second, "2m" for 2 minutes). Specifies how often the
            task should be executed.
        :param main_fn: The main function is to be executed at the specified interval.
        :param host: The host parameter to be passed to the `main_fn` function.
        :param cidr: The CIDR parameter to be passed to the `main_fn` function.
        :param port_scan: The port scanning option or parameter for the `main_fn`
            function.
        :param verbose: Flag indicating whether verbose output is enabled. Passed
            to the `main_fn` function.
        :param check: A parameter indicating the type or condition of checks to
            perform. Passed to the `main_fn` function.
        :param timeout: Time (in seconds or other units) to be passed to the
            `main_fn` function for timeout purposes.
        :param extended_port_scan: Flag or parameter indicating whether an extended
            port scan is to be performed. Passed to the `main_fn` function.
        :return: None
        """

        schedule.every(self.get_schedule_value_in_seconds(schedule_value)).seconds.do(
            partial(
                main_fn,
                host=host,
                cidr=cidr,
                port_scan=port_scan,
                verbose=verbose,
                check=check,
                timeout=timeout,
                extended_port_scan=extended_port_scan,
            )
        )

        while True:
            schedule.run_pending()
            self.show_timer_bar(self.get_schedule_value_in_seconds(schedule_value))

    def get_schedule_value_in_seconds(self, schedule_value: str) -> int | None:
        """
        Get the schedule value in seconds, will handle either minutes or hours
        :param schedule_value: the schedule value to convert to seconds, e.g. "1m" or "1h"
        :return: the value in seconds or nothing
        """
        if schedule_value not in self._available_schedules:
            rich.print(
                TyperOutputBuilder()
                .add_exclamation_mark()
                .apply_bold_red(f"Invalid schedule '{schedule_value}', must be one of: {self._available_schedules}")
                .build()
            )
            exit(1)

        if "m" in schedule_value:
            return int(schedule_value.replace("m", "")) * 60
        if "h" in schedule_value:
            return int(schedule_value.replace("h", "")) * 60 * 60
        return None

    @staticmethod
    def show_timer_bar(duration_seconds: int, update_interval: float = 1.0):
        """
        Display how long is left until the next scan runs to the user
        :param duration_seconds: seconds remaining until the next scan
        :param update_interval: how often to update the timer bar, in seconds. Defaults to 1.0 seconds.
        :return: Nothing will display a timer bar to the user.
        """
        steps = int(duration_seconds / update_interval)
        with Progress(
            "[progress.description]{task.description}",
            BarColumn(complete_style="cyan", finished_style="cyan", style="magenta"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeRemainingColumn(),
            transient=True,
        ) as progress:
            task = progress.add_task("[bold magenta] [+] Time before next scan begins:[/bold magenta]", total=steps)
            for _ in range(steps):
                progress.update(task, advance=1)
                time.sleep(1)
