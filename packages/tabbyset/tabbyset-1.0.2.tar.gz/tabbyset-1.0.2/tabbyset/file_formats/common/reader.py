def split_row(row: list[str], columns_length: int):
    return row[:columns_length], row[columns_length:]


def complete_row(row: list[str], columns_length: int):
    return row + [''] * (columns_length - len(row))


def zip_columns_with_values(columns: list[str], values: list[str]) -> dict[str, str]:
    if len(columns) > len(values):
        values = complete_row(values, len(columns))
    return dict(zip(columns, values))
