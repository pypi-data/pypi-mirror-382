import unittest
import logging
from typing import Optional
from tabbyset.utils.flex_table import FlexTable, ascii_table
from .exceptions import TabbySetDiffFail
from .flex_table_diff import get_flex_tables_diff, get_columns_diff
from .diff import TableCellDiff, ColoredString

logger = logging.getLogger(__name__)

class FlexTableAssertions(unittest.TestCase):
    """
    Class containing assertions for the FlexTable class.

    Usage:

        >>> class TestMyInstrument(FlexTableAssertions):
        >>>     def test_my_instrument(self):
        >>>         table1 = FlexTable()
        >>>         table2 = FlexTable()
        >>>         self.assertFlexTablesEqual(table1, table2)
    """
    def assertFlexTablesEqual(self, table1: FlexTable, table2: FlexTable, msg: Optional[str] = None):
        """
        Assert that two FlexTables are equal. In the case of inequality, custom difference is printed.

        :param table1: The first FlexTable.
        :param table2: The second FlexTable.
        :param msg: The message to display on failure.
        """
        if table1 == table2:
            return
        try:
            columns_diff, merged_columns = get_columns_diff(table1, table2)
            table_diff = get_flex_tables_diff(table1, table2, merged_columns)

            table_data = [columns_diff] + table_diff
            table_width_ref = [
                [
                    len(cell.get_colorized_diff().value) if isinstance(cell, TableCellDiff)
                    else len(cell.value) if isinstance(cell, ColoredString)
                    else len(cell) for cell in row
                ]
                for row in table_data
            ]
        except Exception as e:
            raise TabbySetDiffFail(e)
        if msg:
            added_msg = f"\n: {msg}"
        else:
            added_msg = ""
        self.fail(f"Tables are not equal:\n{ascii_table(table_data, table_width_ref)}{added_msg}")
