from typing import Optional, List, Union, TextIO
from ..abc import AbstractTestCasesReader
from tabbyset.utils.folder import PathParam
from tabbyset.file_formats.common.parsing_logger import FileParsingLogger
from tabbyset.file_formats.exceptions import FileParsingException
from tabbyset.file_formats.common import zip_columns_with_values
from tabbyset.entities.test_case import TestCase
from tabbyset.utils.flex_table import FlexTable
from tabbyset.file_formats.constants import TEST_CASE_END_LABEL, TEST_CASE_START_LABEL


class Csv1Reader(AbstractTestCasesReader):
    """
    A reader for the CSV1 format.

    Csv1Reader is iterable. All Python iteration methods are supported.
    In order  to iterate over all test cases, you also can use `for` loop:

    >>> reader = Csv1Reader('path/to/file.csv')
    ... for test_case in reader:
    ...     print(test_case)

    :param file: The path of the file or an open file object.
    """

    def __init__(self, file: Union[PathParam, TextIO],
                 *,
                 tolerant_mode: bool = False,
                 parsing_logger: Optional[FileParsingLogger] = None):
        AbstractTestCasesReader.__init__(self, file, tolerant_mode=tolerant_mode, parsing_logger=parsing_logger)

    def _parse_as_text(self):

        first_column_index = 0

        csvreader = self._prepare_csv_reader()

        current_tc_started = False
        current_tc_ended = False
        current_tc_columns: Optional[List[str]] = None
        current_tc_name: Optional[str] = None
        current_tc_description: Optional[str] = None
        current_tc_instrument: Optional[str] = None
        current_tc_steps: List[dict[str, str]] = []

        line_number = 0
        test_case_index = -1

        def create_exception(message: str) -> FileParsingException:
            return self._create_reader_exception(message, line_number)

        def log_context() -> dict:
            return {
                'filepath': self._file_path or 'virtual file',
                'lineno': line_number,
                'test_case_index': test_case_index,
                'original_line': str(orig_row)
            }

        def reset_and_get_test_case():
            nonlocal current_tc_name, current_tc_description, current_tc_columns, current_tc_instrument, current_tc_started, current_tc_ended, current_tc_steps
            if self._parsing_logger:
                if current_tc_name is None:
                    self._parsing_logger.error('Test case name not found', **log_context())
                if current_tc_instrument is None:
                    self._parsing_logger.info('Instrument not found in the test case', **log_context())
            test_case = self._postprocess_test_case(
                test_case=TestCase(name=current_tc_name or 'UNKNOWN',
                                   steps=FlexTable(current_tc_steps),
                                   description=current_tc_description),
                instrument=current_tc_instrument
            )

            current_tc_name = None
            current_tc_description = None
            current_tc_columns = None
            current_tc_instrument = None
            current_tc_started = False
            current_tc_ended = True
            current_tc_steps = []

            return test_case

        for orig_row in csvreader:
            line_number += 1

            row = self._strip_row_right(orig_row)
            row_length = len(row)

            is_name_line = current_tc_name is None and current_tc_started
            is_instrument_line = current_tc_instrument is None and current_tc_name is not None
            is_description_line = current_tc_description is None and current_tc_instrument is not None

            # Skip empty rows
            if ((row_length == 0 or all('' == s for s in row))
                    and not (is_name_line or is_instrument_line or is_description_line)):
                if self._parsing_logger:
                    if current_tc_columns:
                        self._parsing_logger.info('Empty step row', **log_context())
                continue

            first_row_item = row[first_column_index] if row_length > first_column_index else ''

            if first_row_item == TEST_CASE_START_LABEL:
                test_case_index += 1
                if self._parsing_logger:
                    if row_length != 1:
                        self._parsing_logger.info('Row with the start label has more than 1 item', **log_context())
                if current_tc_started:
                    if self._parsing_logger:
                        self._parsing_logger.error('Started test case is started again', **log_context())
                    if not self._tolerant_mode:
                        raise create_exception('Started test case is started again')
                    else:
                        yield reset_and_get_test_case()
                current_tc_ended = False
                current_tc_started = True
                continue

            if first_row_item not in [TEST_CASE_START_LABEL, TEST_CASE_END_LABEL] and current_tc_started:
                # Lookup for name (always goes right after start label)
                if current_tc_name is None:
                    if self._parsing_logger:
                        if row_length != 1:
                            self._parsing_logger.info('Row with the case name has more than 1 item', **log_context())
                    current_tc_name = first_row_item
                    if not current_tc_name:
                        # This is logged during postprocessing
                        if not self._tolerant_mode:
                            raise create_exception('Test case name not found')
                    continue

                # Lookup for instrument (always goes right after name)
                # Can be empty
                if is_instrument_line:
                    # Symbol slot logic is logged during columns reading
                    current_tc_instrument = first_row_item or ''
                    continue

                # Lookup for description (always goes right after instrument)
                # In most cases empty
                if is_description_line:
                    current_tc_description = first_row_item or ''
                    if self._parsing_logger:
                        if not current_tc_description:
                            self._parsing_logger.debug('Description is not specified', **log_context())
                    continue

                if current_tc_columns is None:
                    current_tc_columns = row
                    if 'Symbol' not in current_tc_columns:
                        if self._parsing_logger:
                            self._parsing_logger.warning('Label "Symbol" not found in the columns', **log_context())
                        if not current_tc_instrument:
                            if self._parsing_logger:
                                self._parsing_logger.error('Instrument not defined in the test case', **log_context())
                            if not self._tolerant_mode:
                                raise create_exception('Instrument not defined in the test case')
                    continue
                if self._parsing_logger:
                    if row_length > len(current_tc_columns):
                        self._parsing_logger.info('Step row length has more items than columns', **log_context())
                current_tc_steps.append(
                    zip_columns_with_values(current_tc_columns, row)
                )
                continue

            # Return new testcase and reset data
            if first_row_item == TEST_CASE_END_LABEL:
                if not current_tc_started:
                    if self._parsing_logger:
                        self._parsing_logger.error('Not started case tries to end', **log_context())
                    if not self._tolerant_mode:
                        raise create_exception('Not started case tries to end')

                yield reset_and_get_test_case()
        if current_tc_started and not current_tc_ended:
            if self._parsing_logger:
                self._parsing_logger.error('Last test case is not closed', **log_context())
            if not self._tolerant_mode:
                raise create_exception('Last test case is not closed')
