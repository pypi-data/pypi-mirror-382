from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.string import ListOfStrings


class OrganizationType(StrEnum):
    APPLICATION = "application"
    BRANCH = "branch"
    CLIENT = "client"
    CLINIC = "clinic"
    CORPORATION = "corporation"
    DEPARTMENT = "department"
    DIVISION = "division"
    GOVERNMENT = "government"
    HOSPITAL_SYSTEM = "hospital_system"
    HOSPITAL = "hospital"
    INSURANCE_PROVIDER = "insurance_provider"
    INTERNAL = "internal"
    LABORATORY = "laboratory"
    MEDICAL_GROUP = "medical_group"
    NETWORK = "network"
    PARTNER = "partner"
    PHARMACY = "pharmacy"
    PRIMARY_HEALTH_CARE = "primary_health_care"
    PUBLIC_HEALTH_AGENCY = "public_health_agency"
    REGIONAL_OFFICE = "regional_office"
    REGULAR = "regular"
    RESEARCH_INSTITUTE = "research_institute"
    SUBSIDIARY = "subsidiary"
    THIRD_PARTY_ADMINISTRATOR = "third_party_administrator"
    UNIT = "unit"
    VENDOR = "vendor"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


OrganizationTypeT = TypeVar("OrganizationTypeT", bound=OrganizationType)
OptionalOrganizationType = Optional[OrganizationType]
OptionalOrganizationTypeT = TypeVar(
    "OptionalOrganizationTypeT", bound=OptionalOrganizationType
)
ListOfOrganizationTypes = List[OrganizationType]
ListOfOrganizationTypesT = TypeVar(
    "ListOfOrganizationTypesT", bound=ListOfOrganizationTypes
)
OptionalListOfOrganizationTypes = Optional[ListOfOrganizationTypes]
OptionalListOfOrganizationTypesT = TypeVar(
    "OptionalListOfOrganizationTypesT", bound=OptionalListOfOrganizationTypes
)
SequenceOfOrganizationTypes = Sequence[OrganizationType]
SequenceOfOrganizationTypesT = TypeVar(
    "SequenceOfOrganizationTypesT", bound=SequenceOfOrganizationTypes
)
OptionalSequenceOfOrganizationTypes = Optional[SequenceOfOrganizationTypes]
OptionalSequenceOfOrganizationTypesT = TypeVar(
    "OptionalSequenceOfOrganizationTypesT", bound=OptionalSequenceOfOrganizationTypes
)


class Relation(StrEnum):
    AFFILIATE = "affiliate"
    APPLICATION = "application"
    BRANCH = "branch"
    CLIENT = "client"
    DEPARTMENT = "department"
    DIVISION = "division"
    NETWORK_MEMBER = "network_member"
    PARENT = "parent"
    PARTNER = "partner"
    SUBSIDIARY = "subsidiary"
    VENDOR = "vendor"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


RelationT = TypeVar("RelationT", bound=Relation)
OptionalRelation = Optional[Relation]
OptionalRelationT = TypeVar("OptionalRelationT", bound=OptionalRelation)
ListOfRelations = List[Relation]
ListOfRelationsT = TypeVar("ListOfRelationsT", bound=ListOfRelations)
OptionalListOfRelations = Optional[ListOfRelations]
OptionalListOfRelationsT = TypeVar(
    "OptionalListOfRelationsT", bound=OptionalListOfRelations
)
SequenceOfRelations = Sequence[Relation]
SequenceOfRelationsT = TypeVar("SequenceOfRelationsT", bound=SequenceOfRelations)
OptionalSequenceOfRelations = Optional[SequenceOfRelations]
OptionalSequenceOfRelationsT = TypeVar(
    "OptionalSequenceOfRelationsT", bound=OptionalSequenceOfRelations
)


class Role(StrEnum):
    OWNER = "owner"
    ADMINISTRATOR = "administrator"
    USER = "user"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


RoleT = TypeVar("RoleT", bound=Role)
OptionalRole = Optional[Role]
OptionalRoleT = TypeVar("OptionalRoleT", bound=OptionalRole)
ListOfRoles = List[Role]
ListOfRolesT = TypeVar("ListOfRolesT", bound=ListOfRoles)
OptionalListOfRoles = Optional[ListOfRoles]
OptionalListOfRolesT = TypeVar("OptionalListOfRolesT", bound=OptionalListOfRoles)
SequenceOfRoles = Sequence[Role]
SequenceOfRolesT = TypeVar("SequenceOfRolesT", bound=SequenceOfRoles)
OptionalSequenceOfRoles = Optional[SequenceOfRoles]
OptionalSequenceOfRolesT = TypeVar(
    "OptionalSequenceOfRolesT", bound=OptionalSequenceOfRoles
)
