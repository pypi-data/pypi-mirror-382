from typing import Iterable, Iterator, Union

from tabbyset.entities.test_case import TestCase
from tabbyset.file_formats.csv2.reader import Csv2Reader
from tabbyset.file_formats.abc import AbstractTestCasesReader

class TestCasesPlainReader(Iterable[dict]):
    """
    A utility mapping Test Cases stream to plain CSV stream.
    """

    _test_cases_reader: AbstractTestCasesReader
    _current_test_case: TestCase = None
    _current_steps: Iterator[dict] = None

    def __init__(self, test_cases_reader: AbstractTestCasesReader):
        self._test_cases_reader = test_cases_reader

    @property
    def has_headers(self) -> bool:
        return isinstance(self._test_cases_reader, Csv2Reader)

    @property
    def headers(self) -> Union[list[str], dict[str, list[str]]]:
        if not isinstance(self._test_cases_reader, Csv2Reader):
            raise AttributeError(f"{self._test_cases_reader.__class__.__name__} does not have headers.")
        return self._test_cases_reader.global_columns

    def __iter__(self):
        return self

    def __next__(self):
        if self._current_test_case is None:
            test_case = next(self._test_cases_reader, None)
            if test_case is None:
                raise StopIteration
            self._current_test_case = test_case
            self._current_steps = iter(test_case.steps)
        new_row = next(self._current_steps, None)
        if new_row is None:
            self._current_test_case = None
            return next(self)
        return new_row