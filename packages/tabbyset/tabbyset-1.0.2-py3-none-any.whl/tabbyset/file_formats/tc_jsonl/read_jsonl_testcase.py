import json
from typing import Union, TextIO

from ..abc.source_io import SourceIO
from tabbyset.entities.test_case import TestCase
from tabbyset.utils.folder import PathParam
from tabbyset.db.id_utils import is_valid_id, get_id_from_steps


class _TCJsonlReader(SourceIO):
    def read_test_case(self) -> TestCase:
        textio = self._prepare_textio_readable()
        testcase = TestCase(name='undefined', steps=[])
        for line in textio:
            raw_value = json.loads(line)
            line_type = raw_value.get('$type', {})
            line_data = raw_value.get('$data', {})
            if line_type == 'meta':
                testcase.name = line_data.get('name', 'undefined')
                testcase.description = line_data.get('description', None)
                testcase.id = line_data.get('id', None)
            elif line_type == 'step':
                testcase.steps.append(line_data)
        self.close()
        if not is_valid_id(testcase.id):
            testcase.id = get_id_from_steps(testcase)
        return testcase

def read_jsonl_testcase(file: Union[PathParam, TextIO]) -> TestCase:
    """
    Read a single test case from a JSONL file.
    """
    with _TCJsonlReader(file) as reader:
        return reader.read_test_case()