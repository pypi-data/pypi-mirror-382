from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.string import ListOfStrings


class Environment(StrEnum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


EnvironmentT = TypeVar("EnvironmentT", bound=Environment)
OptionalEnvironment = Optional[Environment]
OptionalEnvironmentT = TypeVar("OptionalEnvironmentT", bound=OptionalEnvironment)
ListOfEnvironments = List[Environment]
ListOfEnvironmentsT = TypeVar("ListOfEnvironmentsT", bound=ListOfEnvironments)
OptionalListOfEnvironments = Optional[ListOfEnvironments]
OptionalListOfEnvironmentsT = TypeVar(
    "OptionalListOfEnvironmentsT", bound=OptionalListOfEnvironments
)
SequenceOfEnvironments = Sequence[Environment]
SequenceOfEnvironmentsT = TypeVar(
    "SequenceOfEnvironmentsT", bound=SequenceOfEnvironments
)
OptionalSequenceOfEnvironments = Optional[SequenceOfEnvironments]
OptionalSequenceOfEnvironmentsT = TypeVar(
    "OptionalSequenceOfEnvironmentsT", bound=OptionalSequenceOfEnvironments
)
