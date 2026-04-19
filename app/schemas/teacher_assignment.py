from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class TeacherAssignmentCreate(BaseModel):
    teacher_id: str
    subject_detail_id: str
    academic_id: str
    hourly_rate: Decimal


class TeacherAssignmentUpdate(BaseModel):
    teacher_id: Optional[str] = None
    subject_detail_id: Optional[str] = None
    academic_id: Optional[str] = None
    hourly_rate: Optional[Decimal] = None


class TeacherAssignmentResponse(BaseModel):
    assignment_id: str
    teacher_id: str
    teacher_name: str
    teacher_lastname: str
    subject_name: str
    level_name: str
    academic_year: str
    hourly_rate: Decimal

    @classmethod
    def model_validate(cls, obj):
        return cls(
            assignment_id=obj.assignment_id,
            teacher_id=obj.teacher_id,
            teacher_name=obj.teacher.teacher_name,
            teacher_lastname=obj.teacher.teacher_lastname,
            subject_name=obj.subject_detail.subject.subject_name,
            level_name=obj.subject_detail.level.level_name,
            academic_year=obj.academic_year.academic_year,
            hourly_rate=obj.hourly_rate,
        )

    model_config = {"from_attributes": True}
