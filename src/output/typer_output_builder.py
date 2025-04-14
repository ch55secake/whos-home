from __future__ import annotations

from typing import Any


class TyperOutputBuilder:
    class _Format:
        def __init__(self, format_str: str = "", is_exit: bool = False):
            self.format: str = format_str
            self.is_exit: bool = is_exit

        def add_format(self, format_str: str):
            self.format: str = self.format + " " + format_str

        def create_clear(self) -> TyperOutputBuilder._Format:
            return TyperOutputBuilder._Format(self.format, is_exit=True)

        def __str__(self):
            return f'[{"/" if self.is_exit else ""}{self.format.strip()}]'

    def __init__(self):
        self.__instructions: list[str | TyperOutputBuilder._Format] = []
        self.__current_formatting: TyperOutputBuilder._Format | None = None

    def set_formatting(self, format_str: str) -> TyperOutputBuilder:
        self.__current_formatting = TyperOutputBuilder._Format(format_str)
        self.__instructions.append(format_str)
        return self

    def add_formatting(self, format_str: str) -> TyperOutputBuilder:
        if self.__current_formatting is None:
            self.__current_formatting = TyperOutputBuilder._Format()
            self.__instructions.append(self.__current_formatting)
        self.__current_formatting.add_format(format_str)
        return self

    def apply_bold(self):
        return self.add_formatting("bold")

    def apply_cyan(self):
        return self.add_formatting("cyan")

    def apply_magenta(self):
        return self.add_formatting("magenta")

    def apply_bold_cyan(self):
        return self.apply_bold().apply_cyan()

    def apply_bold_magenta(self):
        return self.apply_bold().apply_magenta()

    def clear_formatting(self) -> TyperOutputBuilder:
        if self.__instructions is None:
            return self
        self.__instructions.append(self.__current_formatting.create_clear())
        self.__current_formatting = None
        return self

    def add(self, message: Any) -> TyperOutputBuilder:
        self.__instructions.append(str(message))
        return self

    def build(self) -> str:
        if self.__current_formatting is not None:
            self.clear_formatting()
        return "".join(str(i) for i in self.__instructions)
