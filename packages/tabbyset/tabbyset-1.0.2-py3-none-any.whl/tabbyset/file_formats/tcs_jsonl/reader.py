import json
from typing import Union, TextIO
from .tc_to_dict import dict_to_tc
from ..abc import AbstractTestCasesReader
from ..exceptions import FileParsingException
from tabbyset.utils.folder import PathParam


class RawTestCasesReader(AbstractTestCasesReader):
    """
    A reader for the raw test cases stored in JSONL.

    Raw test cases are not limited to specifics of CSV1 or CSV2, but they take much more space.

    RawTestCasesReader is iterable. All Python iteration methods are supported.
    In order  to iterate over all test cases, you also can use `for` loop:

    >>> reader = RawTestCasesReader('path/to/file.csv')
    ... for test_case in reader:
    ...     print(test_case)

    :param file: The path of the file or an open file object.
    """

    def __init__(self, file: Union[PathParam, TextIO]):
        super().__init__(file)

    def _parse_as_text(self):

        jsonl_reader = self._prepare_textio_readable()

        line_number = 0

        def create_exception(message: str) -> FileParsingException:
            return self._create_reader_exception(message, line_number)

        for line in jsonl_reader:
            line_number += 1
            try:
                tc_dict = json.loads(line)
            except json.JSONDecodeError as e:
                raise create_exception(f"Failed to parse JSON: {e}")
            try:
                tc = dict_to_tc(tc_dict)
            except KeyError as e:
                raise create_exception(f"Failed to convert JSON to TestCase: {e}")
            yield tc

