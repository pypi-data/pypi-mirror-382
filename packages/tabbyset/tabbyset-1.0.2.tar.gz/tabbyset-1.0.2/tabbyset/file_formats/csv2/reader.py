import copy
from typing import Optional, List, Union, TextIO
from itertools import zip_longest
from ..abc import AbstractTestCasesReader
from ..common import split_row, complete_row
from ..exceptions import FileParsingException
from tabbyset.file_formats.common.multiheader_csv import MultiheaderConfig
from tabbyset.file_formats.common.multiheader_csv.core import MultiheaderCsvCore
from tabbyset.utils.flex_table.constants import EMPTY_VALUE
from tabbyset.utils.warnings import libwarn
from tabbyset.utils.folder import PathParam
from tabbyset.file_formats.constants import TEST_CASE_END_LABEL, TEST_CASE_START_LABEL
from tabbyset.entities.test_case import TestCase


class Csv2Reader(AbstractTestCasesReader):
    """
    A reader for the CSV2 format.

    Csv2Reader is iterable. All Python iteration methods are supported.
    In order  to iterate over all test cases, you also can use `for` loop:

    >>> reader = Csv2Reader('path/to/file.csv')
    ... for test_case in reader:
    ...     print(test_case)

    :param file: The path of the file or an open file object.
    :param multiheader: The flag to specify explicitly if you want use multiheader or not. Default is None, what means that the reader will decide automatically.
    """
    _multiheader: Optional[bool] = None
    _multiheader_core: MultiheaderCsvCore
    _global_columns: Optional[Union[list[str], dict[str, list[str]]]] = None

    def __init__(self,
                 file: Union[PathParam, TextIO],
                 *_,
                 multiheader: Optional[bool] = None,
                 multiheader_config: Optional[MultiheaderConfig] = None):
        super().__init__(file)
        self._multiheader = multiheader
        if multiheader_config:
            if self._multiheader is False:
                libwarn('The multiheader_config parameter is ignored because the multiheader is not used.',
                        category=RuntimeWarning)
        self._multiheader_core = MultiheaderCsvCore(multiheader_config)

    @property
    def global_columns(self) -> Union[list[str], dict[str, list[str]]]:
        if self._global_columns is None:
            next(self)
            self.restart_reading()
        if self._multiheader:
            result = copy.deepcopy(self._global_columns)
            for key in result:
                result[key].remove('')
            return result
        return self._global_columns


    @classmethod
    def get_default_multiheader_config(cls) -> MultiheaderConfig:
        return MultiheaderCsvCore.config

    @classmethod
    def set_default_multiheader_config(cls, multiheader_config: MultiheaderConfig):
        MultiheaderCsvCore.config = multiheader_config

    def _parse_as_text(self):
        # TODO: Add id parsing
        self._multiheader_core.reset_headers()
        first_column_index = 0

        csvreader = self._prepare_csv_reader()

        united_columns: Optional[List[str]] = None
        columns_definitions_read = False

        current_tc_started = False
        current_tc_ended = False
        current_tc_columns: Optional[List[str]] = None
        current_tc_name: Optional[str] = None
        current_tc_content: List[dict] = []

        line_number = 0

        def create_exception(message: str) -> FileParsingException:
            return self._create_reader_exception(message, line_number)

        for row in csvreader:
            line_number += 1

            row = self._strip_row_right(row)
            row_length = len(row)
            first_row_item = row[first_column_index] if row_length > first_column_index else ''

            if row_length == 0 or all('' == s for s in row):
                continue

            if not columns_definitions_read and first_row_item != TEST_CASE_START_LABEL:
                read_line_multiheader_result = self._multiheader_core.read_line(row)
                is_multiheader_columns = read_line_multiheader_result.is_header
                if self._multiheader is None:
                    self._multiheader = is_multiheader_columns
                if self._multiheader != is_multiheader_columns:
                    if self._multiheader:
                        raise create_exception('Multiheader columns are not defined')
                    else:
                        raise create_exception('Multiheader columns are defined, but multiheader is not enabled')

                if is_multiheader_columns:
                    if read_line_multiheader_result.error_msg:
                        raise create_exception(read_line_multiheader_result.error_msg)
                else:
                    if united_columns is None:
                        united_columns = row
                continue

            # Lookup for name
            if first_row_item == TEST_CASE_START_LABEL:
                # Check if columns are defined
                if not columns_definitions_read:
                    if self._multiheader:
                        if not self._multiheader_core.headers:
                            raise create_exception('Multiheader columns are not defined')
                    else:
                        if united_columns is None:
                            raise create_exception('Columns are not defined')
                    columns_definitions_read = True
                    if self._multiheader:
                        self._global_columns = self._multiheader_core.headers
                    else:
                        self._global_columns = united_columns

                if current_tc_started:
                    raise create_exception('Started test case is started again')
                if row_length <= 1:
                    raise create_exception('Start case row should have at least 2 items')
                current_tc_name = row[first_column_index + 1]
                current_tc_ended = False
                current_tc_started = True
                if not current_tc_name:
                    raise create_exception('Test case name not found')
                continue

            # Add content
            if first_row_item not in [TEST_CASE_START_LABEL, TEST_CASE_END_LABEL] and current_tc_started:
                # Checking table header
                # Multiheader files have no local headers
                if current_tc_columns is None and not self._multiheader:
                    if row_length > len(united_columns):
                        # Trim row if it has more items than columns
                        columns_part, extra_part = split_row(row, len(united_columns))
                        current_tc_columns = columns_part
                        current_tc_content.append(columns_part)
                        # Last part
                        if any(extra_part):
                            raise create_exception(
                                f'Extra test case columns - {extra_part}')
                        continue
                    if row_length < len(united_columns):
                        current_tc_columns = complete_row(row, len(united_columns))
                        continue
                    current_tc_columns = row
                    continue

                if self._multiheader:
                    read_line_multiheader_result = self._multiheader_core.read_line(row)
                    if read_line_multiheader_result.error_msg:
                        raise create_exception(read_line_multiheader_result.error_msg)
                    current_row_columns = read_line_multiheader_result.columns
                else:
                    if current_tc_columns is None:
                        raise create_exception('Columns are not defined for test case')
                    current_row_columns = current_tc_columns

                # Checking table row
                if row_length > len(current_row_columns):
                    # Trim row if it has more items than columns
                    columns_part, extra_part = split_row(row, len(current_row_columns))
                    current_row_as_dict = dict(zip_longest(current_row_columns, columns_part, fillvalue=EMPTY_VALUE))
                else:
                    current_row_as_dict = dict(zip_longest(current_row_columns, row, fillvalue=EMPTY_VALUE))
                if self._multiheader:
                    category_check_result = self._multiheader_core.check_row_category(current_row_as_dict,
                                                                                      read_line_multiheader_result.category)
                    if not category_check_result[0]:
                        raise create_exception(category_check_result[1])
                current_tc_content.append(current_row_as_dict)
                continue

            # Add new testcase and reset data
            if first_row_item == TEST_CASE_END_LABEL:
                if not current_tc_started:
                    raise create_exception('Not started case tries to end')

                new_test_case = self._postprocess_test_case(TestCase(name=current_tc_name, steps=current_tc_content))
                yield new_test_case

                current_tc_columns = None
                current_tc_started = False
                current_tc_ended = True
                current_tc_name = None
                current_tc_content = []
        if current_tc_started and not current_tc_ended:
            raise create_exception('Last test case is not closed')
