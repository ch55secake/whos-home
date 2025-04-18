from __future__ import annotations

import logging
from logging import StreamHandler


class Logger:
    """
    Singleton class for the logger
    """

    _instance = None
    _is_verbose = False

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Logger, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self) -> None:
        self.__logger = logging.Logger("whos-home")

        formatter: logging.Formatter = logging.Formatter("[%(asctime)s - %(name)s]: %(message)s", datefmt="%H:%M:%S")

        self.__logger.setLevel(logging.DEBUG)
        self.__logger.propagate = False
        handler: StreamHandler = logging.StreamHandler()
        handler.setFormatter(formatter)

        self.__logger.addHandler(handler)

    def enable(self):
        self._is_verbose = True

    def debug(self, message: str) -> None:
        """
        Log a debug message
        :param message: the message to log
        :return: nothing, will log a message
        """
        if self._is_verbose:
            self.__logger.debug(message)
