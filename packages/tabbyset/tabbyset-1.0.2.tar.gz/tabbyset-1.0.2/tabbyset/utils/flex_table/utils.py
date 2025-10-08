from .constants import EMPTY_VALUE
from .typing import FlexTableValue, FlexTableRow, TabularData
from collections.abc import Iterable


def dict_row_to_list(row: FlexTableRow, ordered_columns: list[str]) -> list[FlexTableValue]:
    return [row.get(col, EMPTY_VALUE) for col in ordered_columns]


def flex_table_to_tabular_data(columns: list[str], rows: Iterable[FlexTableRow]) -> TabularData:
    tabular_data = [columns]
    for row in rows:
        tabular_data.append(dict_row_to_list(row, columns))
    return tabular_data


def sort_with_priority(items: list[str], *_, first_items: list[str] = None, last_items: list[str] = None) -> list[str]:
    """
    Sorts a list of items with priority.
    The first_items will be placed first, the last_items will be placed last in the provided order.
    :param items: The list of items to sort.
    :param first_items: The items to place first.
    :param last_items: The items to place last.
    """
    if first_items is None:
        first_items = []
    if last_items is None:
        last_items = []

    middle_result_items = list(items)

    first_result_items = []
    for item in first_items:
        if item in items:
            first_result_items.append(item)
            middle_result_items.remove(item)

    last_result_items = []
    for item in last_items:
        if item in items:
            last_result_items.append(item)
            middle_result_items.remove(item)

    return first_result_items + middle_result_items + last_result_items


def ascii_table(data: TabularData, ref_widths_data: list[list[int]] = None) -> str:
    if ref_widths_data is None:
        column_widths = [max(len(str(item)) for item in col) for col in zip(*data)]
    else:
        column_widths = [max(col) for col in zip(*ref_widths_data)]
    result = []
    # Print the data in a tabular format
    for i, row in enumerate(data):
        result.append(" | ".join("{:<{}}".format(item, width) for item, width in zip(row, column_widths)))
        if i == 0:
            result.append("=|=".join("=" * col_w for col_w in column_widths) + "=")
    return "\n".join(result)
