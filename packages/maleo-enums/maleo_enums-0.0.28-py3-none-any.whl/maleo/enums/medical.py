from enum import StrEnum
from typing import List, Optional, Sequence, TypeVar
from maleo.types.string import ListOfStrings


class Role(StrEnum):
    # Level 1: Director category
    DIRECTOR = "director"
    PRESIDENT = "president"
    VICE_PRESIDENT = "vice_president"
    SECRETARY = "secretary"
    TREASURER = "treasurer"
    # Level 1: Management category
    HEAD = "head"
    CEO = "ceo"
    COO = "coo"
    CFO = "cfo"
    CCO = "cco"
    # Level 1: Administration category
    ADMINISTRATOR = "administrator"
    ADMISSION = "admission"
    CASHIER = "cashier"
    CASEMIX = "casemix"
    MEDICAL_RECORD = "medical_record"
    # Level 1: Medical category
    DOCTOR = "doctor"
    NURSE = "nurse"
    MIDWIFE = "midwife"
    # Level 2: Doctor's specialization
    INTERNIST = "internist"
    PEDIATRICIAN = "pediatrician"
    OBSTETRICIAN = "obstetrician"
    GYNECOLOGIST = "gynecologist"
    OBGYN = "obgyn"
    PSYCHIATRIST = "psychiatrist"
    DERMATOLOGIST = "dermatologist"
    NEUROLOGIST = "neurologist"
    CARDIOLOGIST = "cardiologist"
    OPHTHALMOLOGIST = "ophthalmologist"
    RADIOLOGIST = "radiologist"
    ANESTHESIOLOGIST = "anesthesiologist"
    HEMATOLOGIST = "hematologist"
    ENDOCRINOLOGIST = "endocrinologist"
    GASTROENTEROLOGIST = "gastroenterologist"
    NEPHROLOGIST = "nephrologist"
    UROLOGIST = "urologist"
    PULMONOLOGIST = "pulmonologist"
    RHEUMATOLOGIST = "rheumatologist"
    SURGEON = "surgeon"
    # Level 3: Surgeon's specialization
    ORTHOPEDIC_SURGEON = "orthopedic_surgeon"
    # Level 2: Nurse's specialization
    SCRUB_NURSE = "scrub_nurse"
    TRIAGE_NURSE = "triage_nurse"
    ICU_NURSE = "icu_nurse"
    NICU_NURSE = "nicu_nurse"
    OR_NURSE = "or_nurse"
    ER_NURSE = "er_nurse"
    # Level 1: Technical category
    TECHNICIAN = "technician"
    LABORATORY_TECHNICIAN = "laboratory_technician"
    RADIOGRAPHER = "radiographer"
    SONOGRAPHER = "sonographer"
    # Level 1: Therapeutic category
    THERAPIST = "therapist"
    PHYSIOTHERAPIST = "physiotherapist"
    OCCUPATIONAL_THERAPIST = "occupational_therapist"
    SPEECH_THERAPIST = "speech_therapist"
    PSYCHOLOGIST = "psychologist"
    # Level 1: Support category
    PHARMACIST = "pharmacist"
    NUTRITIONIST = "nutritionist"

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


class Service(StrEnum):
    EMERGENCY = "emergency"
    INPATIENT = "inpatient"
    INTENSIVE = "intensive"
    OUTPATIENT = "outpatient"

    @classmethod
    def choices(cls) -> ListOfStrings:
        return [e.value for e in cls]


ServiceT = TypeVar("ServiceT", bound=Service)
OptionalService = Optional[Service]
OptionalServiceT = TypeVar("OptionalServiceT", bound=OptionalService)
ListOfServices = List[Service]
ListOfServicesT = TypeVar("ListOfServicesT", bound=ListOfServices)
OptionalListOfServices = Optional[ListOfServices]
OptionalListOfServicesT = TypeVar(
    "OptionalListOfServicesT", bound=OptionalListOfServices
)
SequenceOfServices = Sequence[Service]
SequenceOfServicesT = TypeVar("SequenceOfServicesT", bound=SequenceOfServices)
OptionalSequenceOfServices = Optional[SequenceOfServices]
OptionalSequenceOfServicesT = TypeVar(
    "OptionalSequenceOfServicesT", bound=OptionalSequenceOfServices
)
