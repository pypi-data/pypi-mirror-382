from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.string import ListOfStrings


class Order(StrEnum):
    ASC = "asc"
    DESC = "desc"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


OrderT = TypeVar("OrderT", bound=Order)
OptionalOrder = Optional[Order]
OptionalOrderT = TypeVar("OptionalOrderT", bound=OptionalOrder)
ListOfOrders = List[Order]
ListOfOrdersT = TypeVar("ListOfOrdersT", bound=ListOfOrders)
OptionalListOfOrders = Optional[ListOfOrders]
OptionalListOfOrdersT = TypeVar("OptionalListOfOrdersT", bound=OptionalListOfOrders)
SequenceOfOrders = Sequence[Order]
SequenceOfOrdersT = TypeVar("SequenceOfOrdersT", bound=SequenceOfOrders)
OptionalSequenceOfOrders = Optional[SequenceOfOrders]
OptionalSequenceOfOrdersT = TypeVar(
    "OptionalSequenceOfOrdersT", bound=OptionalSequenceOfOrders
)
