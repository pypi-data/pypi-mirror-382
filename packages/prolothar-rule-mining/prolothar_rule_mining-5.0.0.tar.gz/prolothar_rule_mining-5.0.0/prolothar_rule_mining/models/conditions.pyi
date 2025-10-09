from typing import Callable, Any
from prolothar_common.models.dataset.instance import Instance
from prolothar_common.models.dataset import Dataset
from prolothar_common.models.dataset.attributes import Attribute
from prolothar_common.func_tools import identity

class Condition:

    def check_instance(self, instance: Instance) -> bool: 
        """returns True iff the given instance fullfils this condition"""
        ...

    def divide_dataset(self, dataset: Dataset) -> tuple[Dataset, Dataset]:
        """splits a dataset into matching and non-matching instances"""
        ...

    def estimate_causal_effect(self, dataset: ClassificationDataset, class_label: str, beta: float = 2.0) -> float:
        """ 
        estimate the causal effect of this condition on the given class_label in the dataset, 
        i.e., P(target = class_label | condition holds) - P(target = class_label | condition does not hold)

        result will be a number between -1 and 1
        -1 is the highest possible negative effect on the class label,
            i.e. instances with this condition do not have the label
        1 is the highest possible positive effect on the class label,
            i.e. instances with this condition have the label        
        """
        ...

    def to_html(self) -> str:
        """
        returns a human readable html string representation of this condition
        """
        ...

    def to_bal(self, attribute_formatter: Callable[[str], str] = identity,
               operator_formatter: Callable[[str], str] = identity,
               join_operator_formatter: Callable[[str], str] = identity,
               numerical_value_formatter: Callable[[float], str] = str,
               categorical_value_formatter: Callable[[Any], str] = str) -> str:
        """
        export to the BAL language of IBM ODM
        """
        ...       

class AttributeCondition(Condition):
    attribute: Attribute
    operator_symbol: str
    value: object

    def check_value(self, tested_value) -> bool:
        ...

class EqualsCondition(AttributeCondition):
    """tests equality of an attribute value"""
    def __init__(self, attribute: Attribute, value): ...

class InCondition(AttributeCondition):
    """tests set membership of an attribute value"""
    def __init__(self, attribute: Attribute, value: set): ...

class GreaterOrEqualCondition(AttributeCondition):
    def __init__(self, attribute: Attribute, value): ...

class GreaterThanCondition(AttributeCondition):
    def __init__(self, attribute: Attribute, value): ...

class LessOrEqualCondition(AttributeCondition):
    def __init__(self, attribute: Attribute, value): ...

class LessThanCondition(AttributeCondition):
    def __init__(self, attribute: Attribute, value): ...

class JoinOperatorCondition(Condition):
    """a condition that joins multiple conditions"""
    conditions: list[Condition]
    join_operator: str

    def __init__(self, conditions: list[Condition], join_operator: str): ...

class OrCondition(JoinOperatorCondition):
    ...

class AndCondition(JoinOperatorCondition):
    ...
    