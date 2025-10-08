from __future__ import annotations

import copy
from typing import Dict, List
from types import MappingProxyType

from .test_case import TestCase


class TestScript:
    name: str
    _test_cases_data: List[TestCase]
    _test_cases_index: Dict[str, TestCase]

    def __init__(self, name: str):
        self.name = name
        self._test_cases_data = []
        self._test_cases_index = {}

    def __copy__(self) -> TestScript:
        new_test_script = TestScript(self.name)
        for tc in self._test_cases_data:
            new_test_script.add_test_case(test_case=tc.copy())
        return new_test_script

    @property
    def test_cases(self) -> MappingProxyType[str, TestCase]:
        return MappingProxyType(self._test_cases_index)

    @property
    def all_columns(self) -> List[str]:
        columns = []
        for tc in self._test_cases_data:
            current_columns = tc.steps.columns
            for column in current_columns:
                if column not in columns:
                    columns.append(column)
        return columns

    def remove_test_case(self, name: str):
        self._test_cases_data.remove(self._test_cases_index[name])
        del self._test_cases_index[name]

    def add_test_case(self, test_case: TestCase):
        self._test_cases_data.append(test_case)
        self._test_cases_index[test_case.name] = test_case

    def copy(self) -> TestScript:
        return copy.copy(self)
