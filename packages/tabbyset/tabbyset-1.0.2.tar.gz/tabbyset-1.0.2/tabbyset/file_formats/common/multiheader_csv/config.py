from dataclasses import dataclass
from typing import Callable, Optional

Categorizer = Callable[[dict], str]


@dataclass(frozen=True)
class MultiheaderConfig:
    row_category_prefix: str
    header_category_postfix: str
    categorizer: Categorizer

    column_before_row_category: Optional[str] = None
