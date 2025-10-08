from typing import Union, TextIO, Callable
from .folder import PathParam

from tabbyset.file_formats.csv1.reader import Csv1Reader
from tabbyset.file_formats.csv1.writer import Csv1Writer
from tabbyset.file_formats.csv2.reader import Csv2Reader
from tabbyset.file_formats.csv2.writer import Csv2Writer
from random import Random

FileParam = Union[PathParam, TextIO]

def shuffle_csv1(input_file: FileParam, output_file: FileParam, *, random_seed: int = None) -> None:
    """
    Shuffle the rows of a CSV1 file and write the result to another file.

    By default, the order depends on the random module's random function and by its seed.

    :param input_file: The path of the input CSV1 file or an open file object.
    :param output_file: The path of the output CSV1 file or an open file object.
    :param random_seed: Optional seed for the random number generator to ensure reproducibility.
    """

    with Csv1Reader(input_file) as reader:
        test_cases = list(reader)
        Random(random_seed).shuffle(test_cases)

    with Csv1Writer(output_file, first_priority_columns=[], last_priority_columns=[]) as writer:
        for test_case in test_cases:
            writer.write(test_case)

def shuffle_csv2(input_file: FileParam, output_file: FileParam, *, random_seed: int = None) -> None:
    """
    Shuffle the rows of a CSV2 file and write the result to another file.

    By default, the order depends on the random module's random function and by its seed.

    :param input_file: The path of the input CSV2 file or an open file object.
    :param output_file: The path of the output CSV2 file or an open file object.
    :param random_seed: Optional seed for the random number generator to ensure reproducibility.
    """

    with Csv2Reader(input_file) as reader:
        headers = reader.global_columns
        test_cases = list(reader)
        Random(random_seed).shuffle(test_cases)

    with Csv2Writer(output_file, global_columns=headers) as writer:
        for test_case in test_cases:
            writer.write(test_case)