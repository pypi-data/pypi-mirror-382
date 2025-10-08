from contextlib import ExitStack
from tabbyset.entities import TestCase
from tabbyset.file_formats.abc.abstract_test_cases_writer import ITestCasesWriter


class MultiTestCaseWriter(ITestCasesWriter):
    """
    A writer that writes test cases to multiple files at ones.

    :param test_case_writers: The writers to write the test cases to.
    """
    def __init__(self, *test_case_writers: ITestCasesWriter):
        self.writers = list(test_case_writers)

    def write(self, test_case: TestCase):
        for writer in self.writers:
            writer.write(test_case)

    def write_many(self, test_cases):
        for writer in self.writers:
            writer.write_many(test_cases)

    def close(self):
        exit_stack = ExitStack()
        for writer in self.writers:
            exit_stack.push(writer)
        exit_stack.close()

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
