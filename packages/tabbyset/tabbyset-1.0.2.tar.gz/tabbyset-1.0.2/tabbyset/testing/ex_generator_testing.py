from typing import Type
from .test_case import TestCaseAssertions
from tabbyset.file_formats.abc.abstract_test_cases_reader import AbstractTestCasesReader
from tabbyset.file_formats import Csv1Reader, Csv2Reader, GlobPatterns
from tabbyset.utils import Folder, PathParam


class ExGeneratorTesting(TestCaseAssertions):
    """
    Class containing unit tests for the generated CSV files.
    """

    def compare_csv1_folders(self, folder1: Folder, folder2: Folder):
        """
        Compare two folders containing CSV1 files.
        """
        csv1_pattern = GlobPatterns.csv1_pattern(deep=True)
        for file1, file2 in zip(folder1.glob(csv1_pattern), folder2.glob(csv1_pattern)):
            with self.subTest(test_suite=file1.name.replace('.csv', '')):
                self.compare_custom_files(file1, file2, reader_class=Csv1Reader)

    def compare_csv2_folders(self, folder1: Folder, folder2: Folder):
        """
        Compare two folders containing CSV2 files.
        """
        csv2_pattern = GlobPatterns.csv2_pattern(deep=True)
        for file1, file2 in zip(folder1.glob(csv2_pattern), folder2.glob(csv2_pattern)):
            with self.subTest(test_suite=file1.name.replace('.matrix.csv', '')):
                self.compare_custom_files(file1, file2, reader_class=Csv2Reader)

    def compare_csv2_multiheader_folders(self, folder1: Folder, folder2: Folder):
        """
        Compare two folders containing CSV2 files with multiheaders.
        """
        csv2_pattern = GlobPatterns.csv2_pattern(deep=True)
        for file1, file2 in zip(folder1.glob(csv2_pattern), folder2.glob(csv2_pattern)):
            with self.subTest(test_suite=file1.name.replace('.matrix.csv', '')):
                self.compare_custom_files(file1, file2, reader_class=Csv2Reader, is_multiheaders=True)

    def compare_custom_files(self,
                             csv1_file1: PathParam,
                             csv1_file2: PathParam,
                             reader_class: Type[AbstractTestCasesReader] = Csv1Reader,
                             is_multiheaders: bool = False):
        if isinstance(reader_class, Csv2Reader) and is_multiheaders:
            reader1 = reader_class(csv1_file1, multiheader=True)
            reader2 = reader_class(csv1_file2, multiheader=True)
        else:
            reader1 = reader_class(csv1_file1)
            reader2 = reader_class(csv1_file2)
        for testcase1, testcase2 in zip(reader1, reader2):
            with self.subTest(test_case=testcase1.name):
                self.assertTestCasesEqual(testcase1, testcase2)
        reader1.close()
        reader2.close()
