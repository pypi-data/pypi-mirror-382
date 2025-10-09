import enum
from typing import Any, List, Union

from fiddler_evals.pydantic_models.base import BaseModel


class QueryConditionType(str, enum.Enum):
    AND = "AND"
    OR = "OR"


class QueryRule(BaseModel):
    field: str
    operator: str
    value: Any


class QueryCondition(BaseModel):
    condition: QueryConditionType = QueryConditionType.AND

    rules: List[Union[QueryRule, "QueryCondition"]]

    def add_rule(self, rule: Union[QueryRule, "QueryCondition"]) -> None:
        """Add a filter rule"""
        self.rules.append(rule)

    def add_rules(self, rules: List[Union[QueryRule, "QueryCondition"]]) -> None:
        """Add multiple filter rules"""
        self.rules.extend(rules)


@enum.unique
class OperatorType(str, enum.Enum):
    ANY = "any"
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    IN = "in"
    NOT_IN = "not_in"
    LESS = "less"
    LESS_OR_EQUAL = "less_or_equal"
    GREATER = "greater"
    GREATER_OR_EQUAL = "greater_or_equal"
    BETWEEN = "between"
    NOT_BETWEEN = "not_between"
    BEGINS_WITH = "begins_with"
    NOT_BEGINS_WITH = "not_begins_with"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    ENDS_WITH = "ends_with"
    NOT_ENDS_WITH = "not_ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
