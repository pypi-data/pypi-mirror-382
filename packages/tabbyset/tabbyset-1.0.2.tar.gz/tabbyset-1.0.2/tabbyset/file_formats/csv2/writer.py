import copy

from typing import Union, TextIO, Optional
from ..abc import AbstractTestCasesWriter
from tabbyset.file_formats.constants import TEST_CASE_END_LABEL, TEST_CASE_START_LABEL
from tabbyset.entities.test_case import TestCase
from ..common import complete_row
from tabbyset.file_formats.common.multiheader_csv import MultiheaderConfig
from tabbyset.file_formats.common.multiheader_csv.core import MultiheaderCsvCore
from tabbyset.utils.warnings import libwarn
from tabbyset.utils.folder import PathParam


class Csv2Writer(AbstractTestCasesWriter):
    """
    A writer for CSV2 test scripts.

    In CSV2 format, the global columns are written only once at the beginning of the file.
    It is necessary to provide the list of global columns to the writer.

    :param file: The path of the file or an open file object.
    :param global_columns: Superset of columns for all test cases in the file. In case of multiheader, it is a dictionary with category names as keys and lists of columns as values.
    :param multiheader: The flag to specify explicitly if you want use multiheader or not. Default is None, what means that the writer will decide automatically.
    :param multiheader_config: The configuration for multiheader. Default is the message type based config.
    """
    _global_columns = []
    _global_columns_written = False
    _multiheader = False
    _multiheader_core: MultiheaderCsvCore

    def __init__(self,
                 file: Union[PathParam, TextIO],
                 global_columns: Union[list[str], dict[str, list[str]]],
                 *_,
                 multiheader: Optional[bool] = None,
                 multiheader_config: Optional[MultiheaderConfig] = None):
        AbstractTestCasesWriter.__init__(self, file)
        self._global_columns = copy.deepcopy(global_columns)
        auto_multiheader = isinstance(global_columns, dict)
        if multiheader is None:
            multiheader = auto_multiheader
        elif multiheader != auto_multiheader:
            if auto_multiheader:
                raise ValueError('The global columns are a dictionary, so the multiheader flag should be None or True.')
            else:
                raise ValueError('The global columns are a list, so the multiheader flag should be None or False.')
        self._multiheader = multiheader
        self._multiheader_core = MultiheaderCsvCore(multiheader_config)
        if self._multiheader:
            self._multiheader_core.set_headers(self._global_columns, writable=True)
        if multiheader_config:
            if not multiheader:
                libwarn('The multiheader_config parameter is ignored because the multiheader is not used.',
                        category=RuntimeWarning)

    @classmethod
    def get_default_multiheader_config(cls) -> MultiheaderConfig:
        return MultiheaderCsvCore.config

    @classmethod
    def set_default_multiheader_config(cls, multiheader_config: MultiheaderConfig):
        MultiheaderCsvCore.config = multiheader_config

    @property
    def _max_cells_in_row(self):
        if self._multiheader:
            return max(len(columns) + 2 for columns in self._global_columns.values())
        return len(self._global_columns)

    def _get_tc_start_row(self, test_case_name: str):
        return complete_row([TEST_CASE_START_LABEL, test_case_name], self._max_cells_in_row)

    def _get_tc_end_row(self):
        return complete_row([TEST_CASE_END_LABEL], self._max_cells_in_row)

    def _write_test_case(self, test_case: TestCase):
        # TODO: Write test case id
        if self._multiheader:
            self._write_test_case_multiheader(test_case)
        else:
            self._write_test_case_classic(test_case)

    def _write_test_case_classic(self, test_case: TestCase):
        writer = self._prepare_csv_writer()

        if not self._global_columns_written:
            writer.writerow(self._global_columns)
            self._global_columns_written = True

        writer.writerow(self._get_tc_start_row(test_case.name))
        writer.writerow([(common_column if (common_column in test_case.steps.columns) else '')
                         for common_column in self._global_columns])
        for step in test_case.steps:
            writer.writerow(self._table_item_as_list(step, self._global_columns))
        writer.writerow(self._get_tc_end_row())

    def _write_test_case_multiheader(self, test_case: TestCase):
        writer = self._prepare_csv_writer()

        if not isinstance(self._global_columns, dict):
            raise ValueError('The global columns should be a dictionary for multiheader.')

        if not self._global_columns_written:
            writer.writerows(self._multiheader_core.generate_headers_definitions())
            self._global_columns_written = True

        writer.writerow(self._get_tc_start_row(test_case.name))
        for step in test_case.steps:
            writer.writerow(
                complete_row(self._multiheader_core.generate_writable_line(step),
                             self._max_cells_in_row)
            )
        writer.writerow(self._get_tc_end_row())
