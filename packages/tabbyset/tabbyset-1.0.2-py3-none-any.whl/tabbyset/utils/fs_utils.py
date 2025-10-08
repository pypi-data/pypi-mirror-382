"""
File system utilities
"""
import os.path
from typing import Literal
from tabbyset.file_formats import Csv1Reader, Csv2Reader
from .folder import Folder, PathParam


FileFormat = Literal['csv1', 'csv2']

def walk_tests_folder(folder_path: PathParam, file_format: FileFormat = 'csv1',
                      *,
                      deep: bool = False):
    """
    Walk through the test cases in a folder.
    :param folder_path: The path of the folder.
    :param file_format: The format of the test cases files.
    :param deep: If True, walk through all subfolders.
    :return: An iterator of tuples with a filepath relative to base folder and its testcases.
    """
    if not os.path.exists(folder_path):
        raise FileNotFoundError(f"Folder {folder_path} does not exist")
    folder = Folder(folder_path)
    if file_format == 'csv1':
        file_pattern = '*.csv'
    elif file_format == 'csv2':
        file_pattern = '*.matrix.csv'
    else:
        raise ValueError(f"Unknown file format {file_format}")
    if deep:
        file_pattern = f'**/{file_pattern}'
    for file in folder.glob(file_pattern):
        rel_path = os.path.relpath(file, folder.path)
        if file_format == 'csv1':
            # CSV1 files have .csv extension, however, we want to skip the matrix files
            # Glob patterns support syntax for excluding files, but its implementation is bugged, so we have to do it manually
            if any(rel_path.endswith(ext) for ext in [".matrix.csv", ".matrix.d.csv", ".matrix.expected.csv",
                                                      ".Input.csv", ".Trace.csv"]):
                continue
            with Csv1Reader(file) as reader:
                for tc in reader:
                    yield rel_path, tc
        elif file_format == 'csv2':
            with Csv2Reader(file) as reader:
                for tc in reader:
                    yield rel_path, tc