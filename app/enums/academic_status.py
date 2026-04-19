from enum import Enum
from sqlalchemy.dialects.mysql import ENUM


class AcademicStatusEnum(str, Enum):
    ACTIVE = "ດໍາເນີນການ"
    COMPLETED = "ສິ້ນສຸດ"

AcademicStatusEnumSQL = ENUM(
    AcademicStatusEnum.ACTIVE,
    AcademicStatusEnum.COMPLETED,
    name="academic_status_enum",
)
