from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation
from typing import Union, Any
from .constants import EMPTY_VALUE

from .typing import FlexTableValue


class QueryStatement(ABC):
    _base_value: FlexTableValue

    def __init__(self, base_value: FlexTableValue):
        self._base_value = self._try_number_cast(base_value)

    def apply(self, v: FlexTableValue) -> bool:
        return self._apply_to_casted(self._try_number_cast(v), self._base_value)

    @classmethod
    @abstractmethod
    def _apply_to_casted(cls, v1: FlexTableValue, v2: FlexTableValue) -> bool:
        pass  # pragma: no cover

    @staticmethod
    def _try_number_cast(v: FlexTableValue) -> FlexTableValue:
        try:
            return Decimal(v)
        except InvalidOperation:
            return v


class Equal(QueryStatement):
    @classmethod
    def _apply_to_casted(cls, v1: FlexTableValue, v2: FlexTableValue) -> bool:
        return v1 == v2


class NotEqual(QueryStatement):
    @classmethod
    def _apply_to_casted(cls, v1: FlexTableValue, v2: FlexTableValue) -> bool:
        return v1 != v2


class GreaterThan(QueryStatement):
    @classmethod
    def _apply_to_casted(cls, v1: FlexTableValue, v2: FlexTableValue) -> bool:
        return v1 > v2


class GreaterThanOrEqual(QueryStatement):
    @classmethod
    def _apply_to_casted(cls, v1: FlexTableValue, v2: FlexTableValue) -> bool:
        return v1 >= v2


class LessThan(QueryStatement):
    @classmethod
    def _apply_to_casted(cls, v1: FlexTableValue, v2: FlexTableValue) -> bool:
        return v1 < v2


class LessThanOrEqual(QueryStatement):
    @classmethod
    def _apply_to_casted(cls, v1: FlexTableValue, v2: FlexTableValue) -> bool:
        return v1 <= v2


ParsableQueryStatement = Union[FlexTableValue, QueryStatement]
DictQuery = dict[str, ParsableQueryStatement]


def parse_query_statement(query: ParsableQueryStatement) -> QueryStatement:
    if isinstance(query, QueryStatement):
        return query
    if not isinstance(query, str):
        return Equal(query)
    if query.startswith('= '):
        return Equal(query[2:])
    if query.startswith('!= '):
        return NotEqual(query[3:])
    if query.startswith('> '):
        return GreaterThan(query[2:])
    if query.startswith('>= '):
        return GreaterThanOrEqual(query[3:])
    if query.startswith('< '):
        return LessThan(query[2:])
    if query.startswith('<= '):
        return LessThanOrEqual(query[3:])
    return Equal(query)


def parse_dict_query(query_dict: DictQuery) -> dict[str, QueryStatement]:
    return {k: parse_query_statement(v) for k, v in query_dict.items()}


def apply_query_to_dict(query_dict: dict[str, QueryStatement], value_dict: dict[str, FlexTableValue]) -> bool:
    return all(q.apply(value_dict.get(k, EMPTY_VALUE)) for k, q in query_dict.items())
