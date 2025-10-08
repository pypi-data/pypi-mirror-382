import copy
from collections.abc import Iterable, Mapping, Sequence, Callable
from typing import Union, overload, Any

from tabbyset.utils.flex_table.table_queries import parse_dict_query, QueryStatement, apply_query_to_dict, DictQuery
from tabbyset.utils.dhash import dhash
from .typing import FlexTableValue, FlexTableRow
from .utils import flex_table_to_tabular_data, ascii_table
from .constants import EMPTY_VALUE

Query = dict[str, Union[QueryStatement, FlexTableValue]]
Entry = Mapping[str, FlexTableValue]


class FlexTable(Sequence[FlexTableRow]):
    """
    Class representing a table with flexible columns.

    Flexible columns mean that each row can have different columns.

    :param rows: The rows of the table.
    """
    _data: list[FlexTableRow]

    @property
    def columns(self):
        """
        :return: The list of table columns names.
        """
        columns: dict[str, None] = {}
        for row in self._data:
            for key in row:
                if key not in columns:
                    columns[key] = None
        return list(columns.keys())

    @property
    def EMPTY_VALUE(self):
        """
        :return: The value representing an empty cell.
        """
        return EMPTY_VALUE

    @property
    def rows(self):
        """
        :return: The list of table rows.
        """
        return self._data

    def __init__(self, rows: Iterable[FlexTableRow] = None) -> None:
        if rows is None:
            rows = []
        self._data = []
        self.extend(rows)

    def query(self, query: Query) -> 'FlexTable':
        """
        Queries the table with the given query.

        Custom queries are supported and can be used both for `for` loops and `in` statements.

            >>> table: FlexTable

        - If <query> in FlexTable:
            >>> if {"Action": "Quote"} in table:
            >>>     # Do something, if there is a row with "Action" equal to "Quote"
        - For row in FlexTable[<query>]:
            >>> for row in table.query({"Action": "Quote"}):
            >>>     # Do something with each row with "Action" equal to "Quote"

        **Numbers**

        All the string values are converted to numbers if possible. So the following queries are equal:
            >>> table.query({"Price": "100"})
            >>> table.query({"Price": 100})

        Therefore, query statements can be used with numbers as well:
            >>> table.query({"Price": "> 100"})
            >>> table.query({"Price": "> 100.0"})

        As comparison of the float numbers is not always precise, it is recommended to use strings for float numbers:
            >>> table.query({"Price": "100.0"})

        **Query statements**

        Query statements can be:

        - Equal value (`"<value>"`, `"= <value>"`)
            >>> table.query({"Action": "Quote"})
            >>> table.query({"Action": "= Quote"})
        - Not equal value (`"!= <value>"`)
            >>> table.query({"Action": "!= Quote"})
        - Greater than value (`"> <value>"`)
            >>> table.query({"Price": "> 100"})
        - Greater than or equal value (`">= <value>"`)
            >>> table.query({"Price": ">= 100"})
        - Less than value (`"< <value>"`)
            >>> table.query({"Price": "< 100"})
        - Less than or equal value (`"<= <value>"`)
            >>> table.query({"Price": "<= 100"})

        **Multiple keys**

        If query dictionary contains multiple keys, all of them should be satisfied (acts as `AND` statement).

        For example, the following will return all rows with "Action" equal to "Quote" and "Price" greater than 100.:
            >>> table.query({"Action": "Quote", "Price": "> 100"})
        """
        return self._query(query)

    def _query(self, query: DictQuery) -> 'FlexTable':
        if isinstance(query, dict):
            query = parse_dict_query(query)
            return FlexTable([row for row in self._data if apply_query_to_dict(query, row)])
        raise TypeError(f"Invalid query type: {type(query)}")

    def column_values(self, column: str) -> list[FlexTableValue]:
        """
        :return: The list of values in the given column.
        """
        return self._column_values(column)

    def _column_values(self, column: str) -> list[FlexTableValue]:
        if not isinstance(column, str):
            raise TypeError(f"Invalid column name type: {type(column)}")
        return [row.get(column, EMPTY_VALUE) for row in self._data]

    def contains(self, query: DictQuery) -> bool:
        """
        Checks if the table contains rows matching with the given query.
        """
        return self.__contains__(query)

    def insert(self, idx: int, row: Entry) -> 'FlexTable':
        """
        Inserts a row to the table at the given index.
        returns: The table itself.
        """
        self._data.insert(idx, self._format_entry(row))
        return self

    def append(self, row: Entry) -> 'FlexTable':
        """
        Appends a row to the table.
        """
        self._data.append(self._format_entry(row))
        return self

    def extend(self, rows: Iterable[Entry]) -> 'FlexTable':
        """
        Extends the table with the given rows.
        """
        for row in rows:
            self.append(row)
        return self

    def count(self, query: Query) -> int:
        """
        :return: The number of rows matching the given query.
        """
        return len(self.query(query))

    def index(self, query: Query, start = 0, stop: int = None) -> int:
        """
        :return: The index of the first occurrence of the value in the table.

        If the value is not found, a ValueError is raised.
        """
        for i in range(start, stop or len(self)):
            if apply_query_to_dict(parse_dict_query(query), self[i]):
                return i
        raise ValueError(f"Value not found: {query}")

    def pop(self, idx: int = -1) -> FlexTableRow:
        """
        Removes the row at the given index (default last) and returns it.
        """
        return self._data.pop(idx)

    def remove(self, query: Query) -> 'FlexTable':
        """
        Removes the rows matching the given query.
        """
        self._data = [row for row in self._data if not apply_query_to_dict(parse_dict_query(query), row)]
        return self

    def clear(self) -> None:
        """
        Clears the table.
        """
        self._data.clear()

    def reverse(self) -> 'FlexTable':
        """
        Reverses the table.
        """
        self._data.reverse()
        return self

    def sort(self, *, key: Callable[[FlexTableRow], Any]=None, reverse=False) -> 'FlexTable':
        """
        Sorts the table.
        """
        self._data.sort(key=key, reverse=reverse)
        return self

    def remove_column(self, column: str) -> None:
        """
        Removes the given column from all the rows of the table.
        """
        self.remove_columns((column,))

    def remove_columns(self, columns: Iterable[str]) -> None:
        """
        Removes the given columns from all the rows of the table.
        """
        for row in self._data:
            for column in columns:
                row.pop(column, None)

    def copy(self, deep: bool = False) -> 'FlexTable':
        """
        :return: A copy of the table.
        """
        if deep:
            return copy.deepcopy(self)
        return copy.copy(self)

    def as_ascii_table(self):
        """
        :return: The table as an ASCII table to be printed in the console.
        """
        return ascii_table(flex_table_to_tabular_data(self.columns, self))

    def __eq__(self, other):
        if not isinstance(other, FlexTable):
            return NotImplemented
        return sorted(self.columns) == sorted(other.columns) and tuple(self) == tuple(other)

    def __repr__(self):
        return f'FlexTable({self._data})'

    def __len__(self):
        return len(self._data)

    def __setitem__(self, idx: Union[int, str], value):
        if isinstance(idx, int):
            self._data[idx] = dict(value)
            return
        if isinstance(idx, str):
            for row in self._data:
                row[idx] = value
            return
        raise TypeError("Invalid index type")

    @overload
    def __getitem__(self, idx: int) -> FlexTableRow:
        pass

    @overload
    def __getitem__(self, idx: slice) -> 'FlexTable':
        pass

    @overload
    def __getitem__(self, idx: str) -> list[FlexTableValue]:
        pass

    @overload
    def __getitem__(self, idx: DictQuery) -> 'FlexTable':
        pass

    def __getitem__(self,
                    idx: Union[int, slice, str, FlexTableRow, DictQuery]
                    ) -> Union[FlexTableRow, 'FlexTable', list[FlexTableValue]]:
        if isinstance(idx, int):
            return self._data[idx]
        if isinstance(idx, slice):
            return FlexTable(self._data[idx])
        if isinstance(idx, str):
            return self._column_values(idx)
        if isinstance(idx, dict):
            return self._query(idx)
        raise TypeError(f"Invalid index type: {type(idx)}")

    def __delitem__(self, idx: Union[int, str]):
        if isinstance(idx, int):
            del self._data[idx]
            return
        if isinstance(idx, str):
            self.remove_column(idx)
            return

    def __iter__(self):
        return iter(self._data)

    def __contains__(self, item: DictQuery) -> bool:
        query = parse_dict_query(item)
        for it in self._data:
            if apply_query_to_dict(query, it):
                return True

    def __copy__(self):
        new_instance = FlexTable(self._data.copy())
        return new_instance

    def __deepcopy__(self, memodict=None):
        new_instance = FlexTable(copy.deepcopy(self._data, memodict))
        return new_instance

    def __add__(self,
                other: Union[
                    'FlexTable',
                    Entry,
                    Iterable[Entry]
                ]) -> 'FlexTable':
        new_instance = self.copy()
        self._add_generic(new_instance, other)
        return new_instance

    def __iadd__(self, other: Union[
        'FlexTable',
        Entry,
        Iterable[Entry]
    ]):
        self._add_generic(self, other)
        return self

    def __hash__(self) -> int:
        columns = self.columns
        meaningful_columns = set(columns)
        for column in set(columns):
            if not any(self.column_values(column)):
                meaningful_columns.remove(column)
        meaningful_columns = sorted(meaningful_columns)
        tabular_data = flex_table_to_tabular_data(meaningful_columns, self)
        tabular_data = tuple(tuple(row) for row in tabular_data)
        return dhash(tabular_data)

    @staticmethod
    def _add_generic(table: 'FlexTable', other: Union[
        'FlexTable',
        Entry,
        Iterable[Entry]
    ]) -> 'FlexTable':
        if isinstance(other, FlexTable):
            return table.extend(other)
        if isinstance(other, Mapping):
            return table.append(other)
        if isinstance(other, Iterable):
            return table.extend(other)
        raise TypeError(f"Invalid type: {type(other)}")

    @staticmethod
    def _format_entry(entry: Entry) -> dict:
        if not isinstance(entry, dict):
            entry = dict(entry)
        return entry
