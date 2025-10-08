from typing import Union, TextIO
from ..abc import AbstractTestCasesWriter
from ...utils.flex_table.utils import sort_with_priority
from tabbyset.utils.folder import PathParam
from tabbyset.file_formats.constants import TEST_CASE_END_LABEL, TEST_CASE_START_LABEL
from tabbyset.entities.test_case import TestCase


class Csv1Writer(AbstractTestCasesWriter):
    """
    A writer for CSV1 test scripts.
    :param file: The path of the file or an open file object.
    :param first_priority_columns: The columns that should be written first. Default: `['Status', 'ID', 'PreviousID', 'Action', 'User', 'Symbol', 'Side', 'OrderType', 'TIF', 'OrderQty', 'Price']`.
    :param last_priority_columns: The columns that should be written last. Default: `[]`.
    """

    # Default values are stored in the tuple to prevent modification of the default values.
    _first_priority_columns: list[str]
    _default_first_priority_columns = ('Status', 'ID', 'PreviousID', 'Action', 'User', 'Symbol', 'Side',
                                       'OrderType', 'TIF', 'OrderQty', 'Price')
    _last_priority_columns: list[str]
    _default_last_priority_columns: tuple[str] = tuple()

    def __init__(self,
                 file: Union[PathParam, TextIO],
                 *_,
                 first_priority_columns: list[str] = None,
                 last_priority_columns: list[str] = None):
        AbstractTestCasesWriter.__init__(self, file)
        if first_priority_columns is not None:
            self._first_priority_columns = first_priority_columns
        else:
            self._first_priority_columns = list(self._default_first_priority_columns)
        if last_priority_columns is not None:
            self._last_priority_columns = last_priority_columns
        else:
            self._last_priority_columns = list(self._default_last_priority_columns)

    def _write_test_case(self, test_case: TestCase):
        writer = self._prepare_csv_writer()

        test_case_columns = sort_with_priority(test_case.steps.columns,
                                               first_items=self._first_priority_columns,
                                               last_items=self._last_priority_columns)

        writer.writerow([TEST_CASE_START_LABEL])
        writer.writerow([test_case.name])
        writer.writerow([test_case.id])
        writer.writerow([test_case.description] if test_case.description else [])
        writer.writerow(test_case_columns)
        for step in test_case.steps:
            writer.writerow(self._table_item_as_list(step, test_case_columns))
        writer.writerow([TEST_CASE_END_LABEL])
        writer.writerow([])
        writer.writerow([])
