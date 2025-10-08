from decimal import Decimal
from typing import Union

FlexTableValue = Union[str, int, float, Decimal, None]
FlexTableRow = dict[str, FlexTableValue]
TabularData = list[list[FlexTableValue]]