from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.string import ListOfStrings


class UserType(StrEnum):
    PROXY = "proxy"
    REGULAR = "regular"
    SERVICE = "service"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


UserTypeT = TypeVar("UserTypeT", bound=UserType)
OptionalUserType = Optional[UserType]
OptionalUserTypeT = TypeVar("OptionalUserTypeT", bound=OptionalUserType)
ListOfUserTypes = List[UserType]
ListOfUserTypesT = TypeVar("ListOfUserTypesT", bound=ListOfUserTypes)
OptionalListOfUserTypes = Optional[ListOfUserTypes]
OptionalListOfUserTypesT = TypeVar(
    "OptionalListOfUserTypesT", bound=OptionalListOfUserTypes
)
SequenceOfUserTypes = Sequence[UserType]
SequenceOfUserTypesT = TypeVar("SequenceOfUserTypesT", bound=SequenceOfUserTypes)
OptionalSequenceOfUserTypes = Optional[SequenceOfUserTypes]
OptionalSequenceOfUserTypesT = TypeVar(
    "OptionalSequenceOfUserTypesT", bound=OptionalSequenceOfUserTypes
)
