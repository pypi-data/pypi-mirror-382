from tabbyset.utils.flex_table import FlexTableValue
from enum import Enum
from typing import Optional


class ConsoleColor(Enum):
    RED = "31"
    GREEN = "32"
    YELLOW = "33"
    BLUE = "34"
    MAGENTA = "35"
    CYAN = "36"
    WHITE = "37"
    GRAY = "90"


class ColoredString:
    def __init__(self, value: str, color: ConsoleColor):
        if not isinstance(value, str):
            raise TypeError(f"Value must be a string ({value})")
        if not isinstance(color, ConsoleColor):
            raise TypeError(f"Color must be a ConsoleColor ({color})")
        self.value = value
        self.color = color

    def __len__(self):
        return len(self.value)

    def _before(self):
        return f"\033[{self.color.value}m"

    def _after(self):
        return "\033[0m"

    def __str__(self):
        return f"{self.color.name}<{self.value}>"

    def __repr__(self):
        return f"{self._before()}{self.value}{self._after()}"

    def __format__(self, format_spec):
        return f"{self._before()}{format(self.value, format_spec)}{self._after()}"


class DiffEnum(Enum):
    ADD = "add"
    REMOVE = "remove"
    CHANGE = "change"


class TableCellDiff:
    def __init__(self,
                 added_value: Optional[FlexTableValue] = None,
                 removed_value: Optional[FlexTableValue] = None):
        self.added_value = added_value
        self.removed_value = removed_value

    def get_diff_type(self):
        if self.added_value and self.removed_value:
            return DiffEnum.CHANGE
        if self.added_value:
            return DiffEnum.ADD
        if self.removed_value:
            return DiffEnum.REMOVE
        if self.added_value is not None:
            return DiffEnum.ADD
        if self.removed_value is not None:
            return DiffEnum.REMOVE
        return None

    def __str__(self):
        return str(self.get_colorized_diff())

    def __repr__(self):
        return repr(self.get_colorized_diff())

    def get_colorized_diff(self):
        diff_type = self.get_diff_type()
        if diff_type == DiffEnum.ADD:
            s = f"+{self.added_value}" if self.added_value != '' else '+""'
            return ColoredString(s, ConsoleColor.GREEN)
        if diff_type == DiffEnum.REMOVE:
            s = f"-{self.removed_value}" if self.removed_value != '' else '-""'
            return ColoredString(s, ConsoleColor.MAGENTA)
        return ColoredString(f"{self.removed_value} -> {self.added_value}", ConsoleColor.YELLOW)

    def __format__(self, format_spec):
        return format(self.get_colorized_diff(), format_spec)

