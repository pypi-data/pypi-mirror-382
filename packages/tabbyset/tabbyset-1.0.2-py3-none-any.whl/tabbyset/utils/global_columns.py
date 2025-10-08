from typing import Union
from collections.abc import Iterable
from tabbyset.entities.test_case import TestCase
from tabbyset.utils.flex_table import FlexTable
from tabbyset.file_formats.common.multiheader_csv.config import Categorizer
from tabbyset.file_formats.common.multiheader_csv.core import MultiheaderCsvCore


def _get_global_columns_multiheader(tables: Iterable[Iterable[dict]],
                                    categorizer: Categorizer) -> dict[str, list[str]]:
    categorized_columns: dict[str, dict[str, None]] = {}
    for table in tables:
        if not isinstance(table, FlexTable):
            table = FlexTable(table)
        for row in table:
            category_name = categorizer(row)
            if category_name not in categorized_columns:
                categorized_columns[category_name] = {}
            for column in row:
                if column in categorized_columns[category_name]:
                    continue
                categorized_columns[category_name][column] = None
    return {category_name: list(columns.keys()) for category_name, columns in categorized_columns.items()}


def _get_global_columns_plain(tables: Iterable[Iterable[dict]]) -> list[str]:
    CATEGORY_LABEL = 'UNDEFINED'
    categorized_columns = _get_global_columns_multiheader(tables=tables, categorizer=lambda _: CATEGORY_LABEL)
    return categorized_columns.get(CATEGORY_LABEL, [])


def global_columns(data: Iterable[Union[Iterable[dict], TestCase]],
                   *_,
                   multiheader: bool = False,
                   categorizer: Categorizer = None) -> Union[list[str], dict[str, list[str]]]:
    """
    Extracts global columns from the sequence of test cases or tables.
    :param data: The sequence of test cases or tables.
    :param multiheader: The flag to extract columns with multiheader. Default is False.
    :param categorizer: The function to categorize columns. Default is based on the message type.
    :return: The list of global columns (multiheader=False) or the dictionary of global columns by category (multiheader=True).
    """
    if categorizer is None:
        categorizer = MultiheaderCsvCore.config.categorizer
    tables = (table.steps if isinstance(table, TestCase) else table for table in data)
    if multiheader:
        return _get_global_columns_multiheader(tables, categorizer)
    return _get_global_columns_plain(tables)
