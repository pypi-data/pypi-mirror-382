from typing import Optional

from tabbyset.testing.flex_table import FlexTableAssertions
from tabbyset.utils.flex_table.constants import EMPTY_VALUE
from tabbyset.entities import TestCase


def drop_empty_columns(table):
    for column in table.columns:
        if all(value == EMPTY_VALUE for value in table[column]):
            table.remove_column(column)


class TestCaseAssertions(FlexTableAssertions):
    """
    Class containing assertions for the TestCase class.

    Usage:

        >>> class TestMyInstrument(TestCaseAssertions):
        >>>     def test_my_instrument(self):
        >>>         test_case1 = TestCase("My Test Case", [])
        >>>         test_case2 = TestCase("My Test Case", [])
        >>>         self.assertTestCasesEqual(test_case1, test_case2)
    """

    def assertTestCasesEqual(self, tc1: TestCase, tc2: TestCase, msg: Optional[str] = None):
        """
        Assert that two TestCases are equal. In the case of inequality of steps, custom difference is printed.

        :param tc1: The first TestCase.
        :param tc2: The second TestCase.
        :param msg: The message to display on failure.
        """
        self.assertEqual(tc1.name, tc2.name, msg)
        drop_empty_columns(tc1.steps)
        drop_empty_columns(tc2.steps)
        self.assertFlexTablesEqual(
            tc1.steps, tc2.steps,
            msg=f'Actual steps are not equal to the expected ones in the test case "{tc1.name}"! {msg or ""}'
        )
