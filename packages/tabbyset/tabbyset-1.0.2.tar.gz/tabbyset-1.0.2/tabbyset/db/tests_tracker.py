from typing import Sequence, Literal
from tabbyset.utils.folder import PathParam, Folder
from tabbyset.utils.global_columns import global_columns
from tabbyset.file_formats.glob_patterns import GlobPatterns
from tabbyset.entities import TestCase
from tabbyset.file_formats.csv1 import Csv1Reader, Csv1Writer
from tabbyset.file_formats.csv2 import Csv2Reader, Csv2Writer
from .id_utils import new_id, is_valid_id, get_id_from_steps, NAMESPACE_TEST_CASE

FileFormat = Literal['csv1', 'csv2']

class TestsTracker:
    """
    A set of functions for all the most used utilities for operations with tests.
    It also handles the IDs of the tests to keep them consistent.
    """
    NAMESPACE_TEST_CASE = NAMESPACE_TEST_CASE

    new_id = new_id
    is_valid_id = is_valid_id
    get_id_from_steps = get_id_from_steps

    @classmethod
    def new_test(cls,
                 name: str,
                 steps: Sequence[dict],
                 description: str = '' ) -> TestCase:
        """
        Creates a new test with a new ID.
        """
        return TestCase(name=name, steps=steps, description=description, id=cls.new_id())

    @classmethod
    def copy_test(cls, test: TestCase) -> TestCase:
        """
        Creates a copy of the test WITHOUT changing its ID.
        """
        return test.copy()

    @classmethod
    def fork_test(cls, test: TestCase) -> TestCase:
        """
        Creates a copy of the test WITH a new ID.
        """
        test_copy = test.copy()
        test_copy.id = cls.new_id()
        return test_copy

    @classmethod
    def read_file(cls, file_path: PathParam, file_format: FileFormat = 'csv1') -> list[TestCase]:
        """
        Reads tests from a file.
        """
        if file_format == 'csv1':
            with Csv1Reader(file_path) as reader:
                return list(reader)
        elif file_format == 'csv2':
            with Csv2Reader(file_path) as reader:
                return list(reader)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")

    @classmethod
    def read_folder(cls, folder_path: PathParam, file_format: FileFormat = 'csv1', deep=False) -> list[TestCase]:
        """
        Reads tests from a folder.
        """
        folder = Folder(folder_path)
        if file_format == 'csv1':
            test_cases = []
            for file in folder.glob(GlobPatterns.csv1_pattern(deep)):
                with Csv1Reader(file) as reader:
                    test_cases.extend(reader)
            return test_cases
        if file_format == 'csv2':
            test_cases = []
            for file in folder.glob(GlobPatterns.csv2_pattern(deep)):
                with Csv2Reader(file) as reader:
                    test_cases.extend(reader)
            return test_cases
        raise ValueError(f"Unsupported file format: {file_format}")

    @classmethod
    def write_to_file(cls, file_path: PathParam, test_cases: Sequence[TestCase], file_format: FileFormat = 'csv1') -> None:
        """
        Writes tests to a file.
        """
        if file_format == 'csv1':
            with Csv1Writer(file_path) as writer:
                writer.write_many(test_cases)
        elif file_format == 'csv2':
            with Csv2Writer(file_path, global_columns=global_columns(test_cases)) as writer:
                writer.write_many(test_cases)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")