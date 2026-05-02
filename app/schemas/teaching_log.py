from pydantic import BaseModel, field_serializer
from typing import Optional, Literal
from datetime import datetime
from decimal import Decimal


def format_datetime(value):
    """Format datetime to DD-MM-YYYY HH:MM string"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y %H:%M")
    return str(value)


class TeachingLogCreate(BaseModel):
    assignment_id: str
    substitute_for_assignment_id: Optional[str] = None
    hourly: Decimal
    status: Optional[Literal['TEACHING', 'ABSENT']] = None


class TeachingLogUpdate(BaseModel):
    assignment_id: Optional[str] = None
    substitute_for_assignment_id: Optional[str] = None
    hourly: Optional[Decimal] = None
    status: Optional[Literal['TEACHING', 'ABSENT']] = None


class TeachingLogResponse(BaseModel):
    teaching_log_id: int
    assignment_id: str
    teacher_id: str
    teacher_name: str
    teacher_lastname: str
    subject_name: str
    level_name: str
    academic_year: str
    teaching_date: Optional[datetime] = None
    hourly: Decimal
    hourly_rate: Decimal
    status: Optional[str] = None
    substitute_for_assignment_id: Optional[str] = None
    substitute_for_teacher_id: Optional[str] = None
    substitute_for_teacher_name: Optional[str] = None
    substitute_for_teacher_lastname: Optional[str] = None
    substitute_for_subject_name: Optional[str] = None
    substitute_for_level_name: Optional[str] = None

    @classmethod
    def model_validate(cls, obj):
        assignment = obj.assignment
        teacher = assignment.teacher
        subject_detail = assignment.subject_detail
        teaching_date = obj.teaching_date
        if isinstance(teaching_date, str) and teaching_date.startswith('0000'):
            teaching_date = None

        sub_assignment = obj.substitute_assignment
        sub_teacher_id = None
        sub_teacher_name = None
        sub_teacher_lastname = None
        sub_subject_name = None
        sub_level_name = None
        if sub_assignment:
            sub_teacher_id = sub_assignment.teacher.teacher_id
            sub_teacher_name = sub_assignment.teacher.teacher_name
            sub_teacher_lastname = sub_assignment.teacher.teacher_lastname
            sub_subject_name = sub_assignment.subject_detail.subject.subject_name
            sub_level_name = sub_assignment.subject_detail.level.level_name

        return cls(
            teaching_log_id=obj.teaching_log_id,
            assignment_id=assignment.assignment_id,
            teacher_id=teacher.teacher_id,
            teacher_name=teacher.teacher_name,
            teacher_lastname=teacher.teacher_lastname,
            subject_name=subject_detail.subject.subject_name,
            level_name=subject_detail.level.level_name,
            academic_year=assignment.academic_year.academic_year,
            teaching_date=teaching_date,
            hourly=obj.hourly,
            hourly_rate=assignment.hourly_rate,
            status=obj.status,
            substitute_for_assignment_id=obj.substitute_for_assignment_id,
            substitute_for_teacher_id=sub_teacher_id,
            substitute_for_teacher_name=sub_teacher_name,
            substitute_for_teacher_lastname=sub_teacher_lastname,
            substitute_for_subject_name=sub_subject_name,
            substitute_for_level_name=sub_level_name,
        )

    model_config = {"from_attributes": True}

    @field_serializer('teaching_date')
    def serialize_teaching_date(self, value):
        if isinstance(value, str) and (value.startswith('0000') or value == ''):
            return None
        return format_datetime(value)
