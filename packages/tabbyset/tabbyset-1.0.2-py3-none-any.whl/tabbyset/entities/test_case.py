from __future__ import annotations
import copy

from ..utils.dhash import dhash
from ..utils.flex_table import FlexTable, FlexTableRow
from typing import List, Union, Optional


class TestCase:
    """
    Class representing an Exactpro internal test case.

    :param name: The name of the test case.
    :param description: The description of the test case (Supported only in CSV1 and is not recommended to use in business logic).
    :param steps: The steps of the test case in the form of table.
    """
    name: str
    description: str
    id: Optional[str]

    _steps: FlexTable

    def __init__(self,
                 name: str,
                 steps: Union[List[FlexTableRow], FlexTable],
                 description: str = '',
                 id: Optional[str] = None):
        self.name = name
        self.set_steps(steps)
        self.description = description
        self.id = id

    @property
    def steps(self) -> FlexTable:
        """
        The steps of the test case in the form of table.  See more in `FlexTable`.
        """
        return self._steps

    @steps.setter
    def steps(self, steps: Union[List[FlexTableRow], FlexTable]) -> None:
        """
        Rewrites the steps of the test case.
        """
        self.set_steps(steps)

    def set_steps(self, steps: Union[List[FlexTableRow], FlexTable]) -> None:
        """
        Rewrites the steps of the test case.
        """
        if not isinstance(steps, FlexTable):
            steps = FlexTable(steps)
        self._steps = steps

    def __eq__(self, other: TestCase) -> bool:
        return self.name == other.name and self.steps == other.steps

    def __repr__(self):
        return f"TestCase(name={repr(self.name)}, steps={self.steps}, id={repr(self.id)})"

    def __copy__(self) -> TestCase:
        return TestCase(name=self.name,
                        steps=self.steps.copy(),
                        description=self.description,
                        id=self.id)

    def __deepcopy__(self, memo) -> TestCase:
        return TestCase(name=self.name,
                        steps=self.steps.copy(deep=True),
                        description=self.description,
                        id=self.id)

    def copy(self) -> TestCase:
        """
        :return: A copy of the test case.
        """
        new_tc = copy.deepcopy(self)
        return new_tc

    def __hash__(self) -> int:
        return dhash(('TestCase', hash(self.steps)))
