from .flex_table.constants import EMPTY_VALUE
from .flex_table.table_queries import (
    Equal as equal,
    NotEqual as not_equal,
    GreaterThan as greater_than,
    GreaterThanOrEqual as greater_than_or_equal,
    LessThan as less_than,
    LessThanOrEqual as less_than_or_equal
)

not_empty = not_equal(EMPTY_VALUE)