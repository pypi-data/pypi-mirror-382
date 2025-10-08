from typing import Sequence, Iterable, Union

from tabbyset.utils.flex_table import FlexTableRow


def group_by(table: Sequence[FlexTableRow], by: Union[str, Iterable[str]], *, count: bool=False) -> dict[tuple, Sequence[FlexTableRow]]:
    """
    Groups the rows of a table by the specified columns.

    Args:
        table (Sequence): Table to group.
        by (Iterable): Iterable column names to group by.

    Returns:
        dict[tuple, Sequence]: Mapping from group key (tuple of column values) to FlexTable of rows in that group.
    """
    if not isinstance(table, Sequence):
        raise TypeError("Table must be a sequential object.")
    if not all(isinstance(row, dict) for row in table):
        raise TypeError("Rows in table must be a dictionaries.")
    if not isinstance(by, Iterable):
        raise TypeError("Columns must be an iterable object of column names.")
    if isinstance(by, str):
        by = [by]

    grouped_table = {}

    for idx, row in enumerate(table):
        key = tuple(row.get(col) for col in by)
        if key not in grouped_table:
            grouped_table[key] = 0 if count else []
        grouped_table[key] += 1 if count else [row]
    return grouped_table
