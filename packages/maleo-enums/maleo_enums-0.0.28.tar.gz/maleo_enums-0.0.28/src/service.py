from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.string import ListOfStrings


class ServiceType(StrEnum):
    BACKEND = "backend"
    FRONTEND = "frontend"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


ServiceTypeT = TypeVar("ServiceTypeT", bound=ServiceType)
OptionalServiceType = Optional[ServiceType]
OptionalServiceTypeT = TypeVar("OptionalServiceTypeT", bound=OptionalServiceType)
ListOfServiceTypes = List[ServiceType]
ListOfServiceTypesT = TypeVar("ListOfServiceTypesT", bound=ListOfServiceTypes)
OptionalListOfServiceTypes = Optional[ListOfServiceTypes]
OptionalListOfServiceTypesT = TypeVar(
    "OptionalListOfServiceTypesT", bound=OptionalListOfServiceTypes
)
SequenceOfServiceTypes = Sequence[ServiceType]
SequenceOfServiceTypesT = TypeVar(
    "SequenceOfServiceTypesT", bound=SequenceOfServiceTypes
)
OptionalSequenceOfServiceTypes = Optional[SequenceOfServiceTypes]
OptionalSequenceOfServiceTypesT = TypeVar(
    "OptionalSequenceOfServiceTypesT", bound=OptionalSequenceOfServiceTypes
)


class Category(StrEnum):
    CORE = "core"
    AI = "ai"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


CategoryT = TypeVar("CategoryT", bound=Category)
OptionalCategory = Optional[Category]
OptionalCategoryT = TypeVar("OptionalCategoryT", bound=OptionalCategory)
ListOfCategories = List[Category]
ListOfCategoriesT = TypeVar("ListOfCategoriesT", bound=ListOfCategories)
OptionalListOfCategories = Optional[ListOfCategories]
OptionalListOfCategoriesT = TypeVar(
    "OptionalListOfCategoriesT", bound=OptionalListOfCategories
)
SequenceOfCategories = Sequence[Category]
SequenceOfCategoriesT = TypeVar("SequenceOfCategoriesT", bound=SequenceOfCategories)
OptionalSequenceOfCategories = Optional[SequenceOfCategories]
OptionalSequenceOfCategoriesT = TypeVar(
    "OptionalSequenceOfCategoriesT", bound=OptionalSequenceOfCategories
)


class ShortKey(StrEnum):
    STUDIO = "studio"
    NEXUS = "nexus"
    TELEMETRY = "telemetry"
    METADATA = "metadata"
    IDENTITY = "identity"
    ACCESS = "access"
    WORKSHOP = "workshop"
    RESEARCH = "research"
    REGISTRY = "registry"
    SOAPIE = "soapie"
    MEDIX = "medix"
    DICOM = "dicom"
    SCRIBE = "scribe"
    CDS = "cds"
    IMAGING = "imaging"
    MCU = "mcu"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


ShortKeyT = TypeVar("ShortKeyT", bound=ShortKey)
OptionalShortKey = Optional[ShortKey]
OptionalShortKeyT = TypeVar("OptionalShortKeyT", bound=OptionalShortKey)
ListOfShortKeys = List[ShortKey]
ListOfShortKeysT = TypeVar("ListOfShortKeysT", bound=ListOfShortKeys)
OptionalListOfShortKeys = Optional[ListOfShortKeys]
OptionalListOfShortKeysT = TypeVar(
    "OptionalListOfShortKeysT", bound=OptionalListOfShortKeys
)
SequenceOfShortKeys = Sequence[ShortKey]
SequenceOfShortKeysT = TypeVar("SequenceOfShortKeysT", bound=SequenceOfShortKeys)
OptionalSequenceOfShortKeys = Optional[SequenceOfShortKeys]
OptionalSequenceOfShortKeysT = TypeVar(
    "OptionalSequenceOfShortKeysT", bound=OptionalSequenceOfShortKeys
)


class Key(StrEnum):
    STUDIO = "maleo-studio"
    NEXUS = "maleo-nexus"
    TELEMETRY = "maleo-telemetry"
    METADATA = "maleo-metadata"
    IDENTITY = "maleo-identity"
    ACCESS = "maleo-access"
    WORKSHOP = "maleo-workshop"
    RESEARCH = "maleo-research"
    REGISTRY = "maleo-registry"
    SOAPIE = "maleo-soapie"
    MEDIX = "maleo-medix"
    DICOM = "maleo-dicom"
    SCRIBE = "maleo-scribe"
    CDS = "maleo-cds"
    IMAGING = "maleo-imaging"
    MCU = "maleo-mcu"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


KeyT = TypeVar("KeyT", bound=Key)
OptionalKey = Optional[Key]
OptionalKeyT = TypeVar("OptionalKeyT", bound=OptionalKey)
ListOfKeys = List[Key]
ListOfKeysT = TypeVar("ListOfKeysT", bound=ListOfKeys)
OptionalListOfKeys = Optional[ListOfKeys]
OptionalListOfKeysT = TypeVar("OptionalListOfKeysT", bound=OptionalListOfKeys)
SequenceOfKeys = Sequence[Key]
SequenceOfKeysT = TypeVar("SequenceOfKeysT", bound=SequenceOfKeys)
OptionalSequenceOfKeys = Optional[SequenceOfKeys]
OptionalSequenceOfKeysT = TypeVar(
    "OptionalSequenceOfKeysT", bound=OptionalSequenceOfKeys
)


class ShortName(StrEnum):
    STUDIO = "Studio"
    NEXUS = "Nexus"
    TELEMETRY = "Telemetry"
    METADATA = "Metadata"
    IDENTITY = "Identity"
    ACCESS = "Access"
    WORKSHOP = "Workshop"
    RESEARCH = "Research"
    REGISTRY = "Registry"
    SOAPIE = "SOAPIE"
    MEDIX = "Medix"
    DICOM = "DICON"
    SCRIBE = "Scribe"
    CDS = "CDS"
    IMAGING = "Imaging"
    MCU = "MCU"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


ShortNameT = TypeVar("ShortNameT", bound=ShortName)
OptionalShortName = Optional[ShortName]
OptionalShortNameT = TypeVar("OptionalShortNameT", bound=OptionalShortName)
ListOfShortNames = List[ShortName]
ListOfShortNamesT = TypeVar("ListOfShortNamesT", bound=ListOfShortNames)
OptionalListOfShortNames = Optional[ListOfShortNames]
OptionalListOfShortNamesT = TypeVar(
    "OptionalListOfShortNamesT", bound=OptionalListOfShortNames
)
SequenceOfShortNames = Sequence[ShortName]
SequenceOfShortNamesT = TypeVar("SequenceOfShortNamesT", bound=SequenceOfShortNames)
OptionalSequenceOfShortNames = Optional[SequenceOfShortNames]
OptionalSequenceOfShortNamesT = TypeVar(
    "OptionalSequenceOfShortNamesT", bound=OptionalSequenceOfShortNames
)


class Name(StrEnum):
    STUDIO = "MaleoStudio"
    NEXUS = "MaleoNexus"
    TELEMETRY = "MaleoTelemetry"
    METADATA = "MaleoMetadata"
    IDENTITY = "MaleoIdentity"
    ACCESS = "MaleoAccess"
    WORKSHOP = "MaleoWorkshop"
    RESEARCH = "MaleoResearch"
    REGISTRY = "MaleoRegistry"
    SOAPIE = "MaleoSOAPIE"
    MEDIX = "MaleoMedix"
    DICOM = "MaleoDICON"
    SCRIBE = "MaleoScribe"
    CDS = "MaleoCDS"
    IMAGING = "MaleoImaging"
    MCU = "MaleoMCU"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


NameT = TypeVar("NameT", bound=Name)
OptionalName = Optional[Name]
OptionalNameT = TypeVar("OptionalNameT", bound=OptionalName)
ListOfNames = List[Name]
ListOfNamesT = TypeVar("ListOfNamesT", bound=ListOfNames)
OptionalListOfNames = Optional[ListOfNames]
OptionalListOfNamesT = TypeVar("OptionalListOfNamesT", bound=OptionalListOfNames)
SequenceOfNames = Sequence[Name]
SequenceOfNamesT = TypeVar("SequenceOfNamesT", bound=SequenceOfNames)
OptionalSequenceOfNames = Optional[SequenceOfNames]
OptionalSequenceOfNamesT = TypeVar(
    "OptionalSequenceOfNamesT", bound=OptionalSequenceOfNames
)
