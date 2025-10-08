from abc import ABC, abstractmethod
from collections.abc import Iterable
from contextlib import AbstractContextManager
from typing import Union, TextIO

from .source_io import SourceIO
from tabbyset.entities.test_case import TestCase
from tabbyset.utils.flex_table import FlexTableRow
from tabbyset.utils.flex_table.utils import dict_row_to_list
from tabbyset.utils.folder import PathParam
from tabbyset.db.id_utils import is_valid_id, new_id


class ITestCasesWriter(AbstractContextManager, ABC):
    @abstractmethod
    def write(self, test_case: TestCase):
        """
        Write a test case to the file.
        :param test_case: The test case to write.
        """
        pass

    @abstractmethod
    def write_many(self, test_cases: Iterable[TestCase]):
        """
        Write sequence of test cases to the file.
        :param test_cases: The list of test cases to write.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close the file.
        """
        pass


class AbstractTestCasesWriter(SourceIO, ITestCasesWriter, ABC):
    """
    An abstract class for writing test scripts to files.

    :param file: The path of the file or an open file object.
    """

    def __init__(self, file: Union[PathParam, TextIO]):
        SourceIO.__init__(self, file)

    def write(self, test_case: TestCase):
        test_case_to_write = test_case
        if not is_valid_id(test_case.id):
            test_case_to_write = test_case.copy()
            test_case_to_write.id = new_id()
        self._write_test_case(test_case_to_write)

    def write_many(self, test_cases: Iterable[TestCase]):
        for test_case in test_cases:
            self.write(test_case)

    @abstractmethod
    def _write_test_case(self, test_case: TestCase):
        pass  # pragma: no cover

    @staticmethod
    def _table_item_as_list(item: FlexTableRow, columns: list[str]):
        return dict_row_to_list(item, columns)
