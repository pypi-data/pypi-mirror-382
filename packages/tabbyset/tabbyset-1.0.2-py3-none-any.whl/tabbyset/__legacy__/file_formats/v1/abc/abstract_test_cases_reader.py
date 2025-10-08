from abc import ABC
from typing import Optional

from tabbyset.file_formats.abc.abstract_test_cases_reader import AbstractTestCasesReader as ATCRBase
from tabbyset.entities.test_case import TestCase


class AbstractTestCasesReader(ATCRBase, ABC):
    @staticmethod
    def _postprocess_test_case(test_case: TestCase, instrument: Optional[str]) -> TestCase:
        if '' in test_case.steps.columns:
            test_case.steps.remove_column('')
        if 'Symbol' not in test_case.steps.columns:
            test_case.steps['Symbol'] = instrument or ''
        return test_case