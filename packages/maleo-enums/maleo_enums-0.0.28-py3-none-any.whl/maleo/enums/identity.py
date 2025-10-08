from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.string import ListOfStrings


class BloodType(StrEnum):
    A = "a"
    B = "b"
    AB = "ab"
    O = "o"  # noqa: E741

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


BloodTypeT = TypeVar("BloodTypeT", bound=BloodType)
OptionalBloodType = Optional[BloodType]
OptionalBloodTypeT = TypeVar("OptionalBloodTypeT", bound=OptionalBloodType)
ListOfBloodTypes = List[BloodType]
ListOfBloodTypesT = TypeVar("ListOfBloodTypesT", bound=ListOfBloodTypes)
OptionalListOfBloodTypes = Optional[ListOfBloodTypes]
OptionalListOfBloodTypesT = TypeVar(
    "OptionalListOfBloodTypesT", bound=OptionalListOfBloodTypes
)
SequenceOfBloodTypes = Sequence[BloodType]
SequenceOfBloodTypesT = TypeVar("SequenceOfBloodTypesT", bound=SequenceOfBloodTypes)
OptionalSequenceOfBloodTypes = Optional[SequenceOfBloodTypes]
OptionalSequenceOfBloodTypesT = TypeVar(
    "OptionalSequenceOfBloodTypesT", bound=OptionalSequenceOfBloodTypes
)


class Gender(StrEnum):
    UNDISCLOSED = "undisclosed"
    FEMALE = "female"
    MALE = "male"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


GenderT = TypeVar("GenderT", bound=Gender)
OptionalGender = Optional[Gender]
OptionalGenderT = TypeVar("OptionalGenderT", bound=OptionalGender)
ListOfGenders = List[Gender]
ListOfGendersT = TypeVar("ListOfGendersT", bound=ListOfGenders)
OptionalListOfGenders = Optional[ListOfGenders]
OptionalListOfGendersT = TypeVar("OptionalListOfGendersT", bound=OptionalListOfGenders)
SequenceOfGenders = Sequence[Gender]
SequenceOfGendersT = TypeVar("SequenceOfGendersT", bound=SequenceOfGenders)
OptionalSequenceOfGenders = Optional[SequenceOfGenders]
OptionalSequenceOfGendersT = TypeVar(
    "OptionalSequenceOfGendersT", bound=OptionalSequenceOfGenders
)
