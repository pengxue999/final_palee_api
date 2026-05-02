from enum import Enum
from sqlalchemy.dialects.mysql import ENUM


class AcademicStatusEnum(str, Enum):
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"

AcademicStatusEnumSQL = ENUM(
    AcademicStatusEnum.ACTIVE,
    AcademicStatusEnum.ENDED,
    name="academic_status_enum",
)
