from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.string import ListOfStrings


class DataStatus(StrEnum):
    DELETED = "deleted"
    INACTIVE = "inactive"
    ACTIVE = "active"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


DataStatusT = TypeVar("DataStatusT", bound=DataStatus)
OptionalDataStatus = Optional[DataStatus]
OptionalDataStatusT = TypeVar("OptionalDataStatusT", bound=OptionalDataStatus)
ListOfDataStatuses = List[DataStatus]
ListOfDataStatusesT = TypeVar("ListOfDataStatusesT", bound=ListOfDataStatuses)
OptionalListOfDataStatuses = Optional[ListOfDataStatuses]
OptionalListOfDataStatusesT = TypeVar(
    "OptionalListOfDataStatusesT", bound=OptionalListOfDataStatuses
)
SequenceOfDataStatuses = Sequence[DataStatus]
SequenceOfDataStatusesT = TypeVar(
    "SequenceOfDataStatusesT", bound=SequenceOfDataStatuses
)
OptionalSequenceOfDataStatuses = Optional[SequenceOfDataStatuses]
OptionalSequenceOfDataStatusesT = TypeVar(
    "OptionalSequenceOfDataStatusesT", bound=OptionalSequenceOfDataStatuses
)


FULL_DATA_STATUSES: SequenceOfDataStatuses = (
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
    DataStatus.DELETED,
)

BASIC_DATA_STATUSES: SequenceOfDataStatuses = (
    DataStatus.ACTIVE,
    DataStatus.INACTIVE,
)
