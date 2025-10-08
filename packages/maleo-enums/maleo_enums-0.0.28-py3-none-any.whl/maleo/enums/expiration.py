from enum import IntEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.integer import ListOfIntegers


class Expiration(IntEnum):
    EXP_15SC = int(15)
    EXP_30SC = int(30)
    EXP_1MN = int(1 * 60)
    EXP_5MN = int(5 * 60)
    EXP_10MN = int(10 * 60)
    EXP_15MN = int(15 * 60)
    EXP_30MN = int(30 * 60)
    EXP_1HR = int(1 * 60 * 60)
    EXP_6HR = int(6 * 60 * 60)
    EXP_12HR = int(12 * 60 * 60)
    EXP_1DY = int(1 * 24 * 60 * 60)
    EXP_3DY = int(3 * 24 * 60 * 60)
    EXP_1WK = int(1 * 7 * 24 * 60 * 60)
    EXP_2WK = int(2 * 7 * 24 * 60 * 60)
    EXP_1MO = int(1 * 30 * 24 * 60 * 60)

    @classmethod
    def choices(cls) -> ListOfIntegers:
        return [e.value for e in cls]


ExpirationT = TypeVar("ExpirationT", bound=Expiration)
OptionalExpiration = Optional[Expiration]
OptionalExpirationT = TypeVar("OptionalExpirationT", bound=OptionalExpiration)
ListOfExpirations = List[Expiration]
ListOfExpirationsT = TypeVar("ListOfExpirationsT", bound=ListOfExpirations)
OptionalListOfExpirations = Optional[ListOfExpirations]
OptionalListOfExpirationsT = TypeVar(
    "OptionalListOfExpirationsT", bound=OptionalListOfExpirations
)
SequenceOfExpirations = Sequence[Expiration]
SequenceOfExpirationsT = TypeVar("SequenceOfExpirationsT", bound=SequenceOfExpirations)
OptionalSequenceOfExpirations = Optional[SequenceOfExpirations]
OptionalSequenceOfExpirationsT = TypeVar(
    "OptionalSequenceOfExpirationsT", bound=OptionalSequenceOfExpirations
)
