import difflib
from decimal import Decimal, InvalidOperation
from tabbyset.utils.flex_table import FlexTable, dict_row_to_list
from typing import Union
from .diff import TableCellDiff, ColoredString, ConsoleColor


def _dict_row_to_formatted_list(row: dict, columns: list[str]) -> list[str]:
    result = []
    for v in dict_row_to_list(row, columns):
        try:
            result.append(str(Decimal(v)))
        except InvalidOperation:
            result.append(str(v))
    return result


def _get_columns_diff_sequence_matcher(expected: FlexTable, actual: FlexTable):
    expected_columns = expected.columns
    actual_columns = actual.columns
    matcher = difflib.SequenceMatcher(None, expected_columns, actual_columns)
    opcodes = matcher.get_opcodes()
    columns_diff = []
    merged_columns = []
    for tag, expected_index_start, expected_index_end, actual_index_start, actual_index_end in opcodes:
        expected_indexes = range(expected_index_start, expected_index_end)
        actual_indexes = range(actual_index_start, actual_index_end)
        if tag == "equal":
            columns_diff += expected_columns[expected_index_start:expected_index_end]
            merged_columns += expected_columns[expected_index_start:expected_index_end]
        elif tag == "replace":
            for expected_index in expected_indexes:
                columns_diff.append(TableCellDiff(added_value=expected_columns[expected_index]))
                merged_columns.append(expected_columns[expected_index])
            for actual_index in actual_indexes:
                columns_diff.append(TableCellDiff(removed_value=actual_columns[actual_index]))
                merged_columns.append(actual_columns[actual_index])
        elif tag == "insert":
            columns_diff += [TableCellDiff(removed_value=actual_columns[j]) for j in actual_indexes]
            merged_columns += [actual_columns[j] for j in actual_indexes]
        elif tag == "delete":
            columns_diff += [TableCellDiff(added_value=expected_columns[i]) for i in expected_indexes]
            merged_columns += [expected_columns[i] for i in expected_indexes]
    return columns_diff, merged_columns


def _get_columns_diff_set(expected: FlexTable, actual: FlexTable):
    expected_columns = set(expected.columns)
    actual_columns = set(actual.columns)
    columns_diff = [TableCellDiff(added_value=column) for column in expected_columns - actual_columns]
    columns_diff += [TableCellDiff(removed_value=column) for column in actual_columns - expected_columns]
    merged_columns = list(expected_columns | actual_columns)
    return columns_diff, merged_columns


def get_columns_diff(table1: FlexTable, table2: FlexTable):
    expected_columns = set(table1.columns)
    actual_columns = set(table2.columns)
    if expected_columns == actual_columns:
        return list(table1.columns), list(table2.columns)
    # Logic for diff is swapped, so it is fixed here
    columns_diff, merged_columns = _get_columns_diff_sequence_matcher(table2, table1)
    if len(merged_columns) > len(expected_columns | actual_columns):
        # Logic for diff is swapped, so it is fixed here
        columns_diff, merged_columns = _get_columns_diff_set(table2, table1)
    return columns_diff, merged_columns


def get_flex_tables_diff(table1: FlexTable, table2: FlexTable, merged_columns: list[str]):
    # Logic for diff is swapped, so it is fixed here
    expected_formatted = [_dict_row_to_formatted_list(row, merged_columns) for row in table2]
    actual_formatted = [_dict_row_to_formatted_list(row, merged_columns) for row in table1]
    old_messages = [str(row) for row in expected_formatted]
    new_messages = [str(row) for row in actual_formatted]
    # Create a SequenceMatcher object
    matcher = difflib.SequenceMatcher(None, old_messages, new_messages)

    # Get the list of operations that transform the old sequence into the new sequence
    opcodes = matcher.get_opcodes()

    table_diff: list[list[Union[TableCellDiff, str, ColoredString]]] = []

    # Iterate over the opcodes
    for tag, expected_index_start, expected_index_end, actual_index_start, actual_index_end in opcodes:
        expected_indexes = range(expected_index_start, expected_index_end)
        actual_indexes = range(actual_index_start, actual_index_end)
        if tag == "equal":
            # The messages are equal, so add a mapping from the old message index to the new message index
            if len(expected_indexes) < 3:
                for expected_index, actual_index in zip(expected_indexes, actual_indexes):
                    table_diff.append(list(expected_formatted[expected_index]))
            else:
                table_diff.append(list(expected_formatted[expected_indexes[0]]))
                table_diff.append([ColoredString("...", ConsoleColor.GRAY) for _ in range(len(merged_columns))])
                table_diff.append(list(expected_formatted[expected_indexes[-1]]))
        elif tag == "replace":
            # The messages are different, so add a mapping from the old message index to the new message index
            for expected_index, actual_index in zip(expected_indexes, actual_indexes):
                table_diff.append([
                    TableCellDiff(
                        removed_value=actual_formatted[actual_index][k],
                        added_value=expected_formatted[expected_index][k]
                    )
                    if actual_formatted[actual_index][k] != expected_formatted[expected_index][k]
                    else expected_formatted[expected_index][k]
                    for k in range(len(merged_columns))
                ])
            if len(expected_indexes) > len(actual_indexes):
                for expected_index_diff in range(len(expected_indexes) - len(actual_indexes)):
                    actual_row_index = actual_index_start + len(actual_indexes) + expected_index_diff
                    if actual_row_index < len(actual_formatted):
                        table_diff.append([TableCellDiff(added_value=actual_formatted[actual_row_index][k])
                                           for k in range(len(merged_columns))])
                    else:
                        expected_row_index = expected_indexes[-expected_index_diff - 1]
                        table_diff.append([TableCellDiff(removed_value=expected_formatted[expected_row_index][k])
                                           for k in range(len(merged_columns))])
            elif len(actual_indexes) > len(expected_indexes):
                for actual_index_diff in range(len(actual_indexes) - len(expected_indexes)):
                    expected_row_index = expected_index_start + len(expected_indexes) + actual_index_diff
                    if expected_row_index < len(expected_formatted):
                        table_diff.append([TableCellDiff(removed_value=expected_formatted[expected_row_index][k])
                                           for k in range(len(merged_columns))])
                    else:
                        actual_row_index = actual_indexes[-actual_index_diff - 1]
                        table_diff.append([TableCellDiff(added_value=actual_formatted[actual_row_index][k])
                                           for k in range(len(merged_columns))])
        elif tag == "insert":
            # The new message is not in the old sequence, so add a mapping from None to the new message index
            for actual_index in actual_indexes:
                table_diff.append(
                    [TableCellDiff(
                        removed_value=actual_formatted[actual_index][k]
                    ) for k in range(len(merged_columns))])
        elif tag == "delete":
            # The old message is not in the new sequence, so add a mapping from the old message index to None
            for expected_index in expected_indexes:
                table_diff.append(
                    [TableCellDiff(
                        added_value=expected_formatted[expected_index][k]
                    ) for k in range(len(merged_columns))])
    return table_diff
