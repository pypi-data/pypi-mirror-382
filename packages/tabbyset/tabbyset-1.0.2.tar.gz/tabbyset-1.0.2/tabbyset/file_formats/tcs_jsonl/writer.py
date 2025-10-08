import json

from typing import Union, TextIO
from .tc_to_dict import tc_to_dict
from ..abc import AbstractTestCasesWriter
from tabbyset.entities.test_case import TestCase
from tabbyset.utils.folder import PathParam


class RawTestCasesWriter(AbstractTestCasesWriter):
    """
    A writer for test scripts in raw JSONL format.

    It is not limited to specifics of CSV1 or CSV2, but takes much more space.
    :param file: The path of the file or an open file object.
    """

    # Default values are stored in the tuple to prevent modification of the default values.

    def __init__(self, file: Union[PathParam, TextIO]):
        AbstractTestCasesWriter.__init__(self, file)

    def _write_test_case(self, test_case: TestCase):
        writer = self._prepare_textio_writable()

        writer.write(json.dumps(tc_to_dict(test_case)))
        writer.write("\n")
