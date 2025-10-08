from abc import ABC, abstractmethod
from collections.abc import Iterator, Iterable
from typing import Optional, Union, Generator, TextIO

from tabbyset.db.id_utils import get_id_from_steps, is_valid_id
from .source_io import SourceIO
from ..exceptions import FileParsingException, VirtualFileParsingException
from tabbyset.file_formats.common.parsing_logger import FileParsingLogger
from tabbyset.entities.test_case import TestCase
from tabbyset.utils.folder import PathParam


class AbstractTestCasesReader(SourceIO, Iterable[TestCase], ABC):
    """
    An abstract class for reading test scripts from files.

    :param file: The path of the file or an open file object.
    """
    _iterator: Optional[Iterator[TestCase]] = None
    _is_iterator_done: bool = False
    _tolerant_mode: bool

    def __init__(self,
                 file: Union[PathParam, TextIO],
                 *,
                 tolerant_mode: bool = False,
                 parsing_logger: Optional[FileParsingLogger] = None):
        SourceIO.__init__(self, file)
        self._tolerant_mode = tolerant_mode
        self._parsing_logger = parsing_logger

    @abstractmethod
    def _parse_as_text(self) -> Generator[TestCase, None, None]:
        pass  # pragma: no cover

    def read_all(self):
        """
        Read all test cases from the file.
        :return: A list of test cases.
        """
        return list(iter(self))

    def read_one(self) -> Optional[TestCase]:
        """
        Read a next test case from the file.

        Updates the internal iterator.

        :return: A test case.
        """
        return next(self, None)

    def restart_reading(self):
        """
        Restart reading from the beginning of the file.
        """
        current_iterator = self._iterator
        if current_iterator is not None:
            del current_iterator
            self._iterator = None
        if self._textio is not None:
            self._textio.seek(self._starting_position)
        self._iterator = self._parse_as_text()

    def check_validity(self) -> bool:
        """
        Check if the file is valid.

        This method restarts reading from the beginning of the file.
        :return: True if the file is valid, False otherwise.
        """
        try:
            self.restart_reading()
            for _ in iter(self):
                pass
            self.restart_reading()
            return True
        except FileParsingException as e:
            self.restart_reading()
            return False

    def __iter__(self) -> Iterator[TestCase]:
        """
        Iterate over test cases in the file.
        :return: An iterator over test cases.
        :raises tabbyset.FileParsingException: If the file is not valid.
        :raises tabbyset.VirtualFileParsingException: If the files content is not valid and filepath is not available.
        """
        if self._iterator is None:
            self.restart_reading()
        return self._iterator

    def __next__(self) -> TestCase:
        return next(iter(self))

    def _create_reader_exception(self, message: str, line_number: int) -> FileParsingException:
        file = self._file_path
        if file:
            return FileParsingException(file_path=file, line_number=line_number, message=message)
        if self._textio is not None:
            self._textio.seek(0)
            file = self._textio.read()
        return VirtualFileParsingException(file=file, line_number=line_number, message=message)

    @staticmethod
    def _postprocess_test_case(test_case: TestCase) -> TestCase:
        if '' in test_case.steps.columns:
            test_case.steps.remove_column('')
        if not is_valid_id(test_case.id or ''):
            test_case.id = get_id_from_steps(test_case)
        return test_case

    @staticmethod
    def _strip_row_right(row: list[str]) -> list[str]:
        for i in range(len(row) - 1, -1, -1):
            if row[i]:
                return row[:i + 1]
        return []
