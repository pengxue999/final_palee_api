from pydantic import BaseModel, field_serializer, Field, field_validator
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


def format_date(value):
    """Format date to YYYY-MM-DD string"""
    if value is None:
        return None
    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")
    return value


def parse_date_input(value):
    if value is None or value == '':
        return None
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        cleaned = value.strip()
        for pattern in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(cleaned, pattern).date()
            except ValueError:
                continue
    raise ValueError('evaluation_date must be a valid date')


class EvaluationCreate(BaseModel):
    semester: str
    evaluation_date: date

    @field_validator('evaluation_date', mode='before')
    @classmethod
    def validate_evaluation_date(cls, value):
        return parse_date_input(value)


class EvaluationUpdate(BaseModel):
    semester: Optional[str] = None
    evaluation_date: Optional[date] = None

    @field_validator('evaluation_date', mode='before')
    @classmethod
    def validate_evaluation_date(cls, value):
        return parse_date_input(value)


class EvaluationResponse(BaseModel):
    evaluation_id: str
    semester: str
    evaluation_date: date

    @classmethod
    def model_validate(cls, obj):
        return cls(
            evaluation_id=obj.evaluation_id,
            semester=str(obj.semester.value if hasattr(obj.semester, "value") else obj.semester),
            evaluation_date=obj.evaluation_date,
        )

    model_config = {"from_attributes": True}

    @field_serializer('evaluation_date')
    def serialize_evaluation_date(self, value):
        return format_date(value)


class EvaluationDetailCreate(BaseModel):
    evaluation_id: str
    regis_detail_id: int
    score: Decimal
    ranking: int = 0
    prize: Optional[Decimal] = None


class EvaluationDetailUpdate(BaseModel):
    evaluation_id: Optional[str] = None
    regis_detail_id: Optional[int] = None
    score: Optional[Decimal] = None
    ranking: Optional[int] = None
    prize: Optional[Decimal] = None


class EvaluationDetailResponse(BaseModel):
    eval_detail_id: int
    evaluation_id: str
    regis_detail_id: int
    registration_id: str
    student_id: str
    student_name: str
    student_lastname: str
    full_name: str
    subject_name: str
    level_name: str
    score: Decimal
    ranking: int
    prize: Optional[Decimal]

    @classmethod
    def model_validate(cls, obj):
        registration = obj.registration_detail.registration
        student = registration.student
        fee = obj.registration_detail.fee_rel
        subject_detail = fee.subject_detail
        return cls(
            eval_detail_id=obj.eval_detail_id,
            evaluation_id=obj.evaluation_id,
            regis_detail_id=obj.regis_detail_id,
            registration_id=registration.registration_id,
            student_id=student.student_id,
            student_name=student.student_name,
            student_lastname=student.student_lastname,
            full_name=f"{student.student_name} {student.student_lastname}".strip(),
            subject_name=subject_detail.subject.subject_name,
            level_name=subject_detail.level.level_name,
            score=obj.score,
            ranking=obj.ranking,
            prize=obj.prize
        )

    model_config = {"from_attributes": True}


class ScoreEntryStudentPayload(BaseModel):
    regis_detail_id: int
    score: Optional[Decimal] = Field(default=None, ge=0, le=100)
    prize: Optional[Decimal | str] = None


class ScoreEntrySubjectResponse(BaseModel):
    subject_id: str
    subject_name: str


class ScoreEntryLevelResponse(BaseModel):
    subject_detail_id: str
    level_id: str
    level_name: str
    fee_amount: Decimal


class ScoreEntrySaveRequest(BaseModel):
    semester: str
    level_id: str
    subject_detail_id: str
    evaluation_date: date
    scores: list[ScoreEntryStudentPayload]

    @field_validator('evaluation_date', mode='before')
    @classmethod
    def validate_evaluation_date(cls, value):
        return parse_date_input(value)


class ScoreEntryStudentResponse(BaseModel):
    regis_detail_id: int
    registration_id: str
    student_id: str
    student_name: str
    student_lastname: str
    full_name: str
    subject_detail_id: str
    subject_id: str
    subject_name: str
    fee_amount: Decimal
    score: Optional[Decimal] = None
    ranking: Optional[int] = None
    prize: Optional[Decimal] = None


class ScoreEntrySummaryResponse(BaseModel):
    total_students: int
    entered_students: int
    missing_students: int
    highest_score: Optional[Decimal] = None
    lowest_score: Optional[Decimal] = None
    average_score: Optional[Decimal] = None


class ScoreEntrySheetResponse(BaseModel):
    academic_id: Optional[str] = None
    academic_year: Optional[str] = None
    semester: str
    level_id: str
    level_name: str
    subject_detail_id: str
    subject_id: str
    subject_name: str
    evaluation_id: Optional[str] = None
    evaluation_date: Optional[date] = None
    summary: ScoreEntrySummaryResponse
    students: list[ScoreEntryStudentResponse]

    @field_serializer('evaluation_date')
    def serialize_sheet_date(self, value):
        if value is None:
            return None
        return value.strftime("%Y-%m-%d")


class AssessmentReportItemResponse(BaseModel):
    evaluation_id: str
    academic_id: Optional[str] = None
    academic_year: Optional[str] = None
    semester: str
    evaluation_type: Optional[str] = None
    subject_id: str
    level_id: str
    student_id: str
    student_name: str
    student_lastname: str
    full_name: str
    province_name: Optional[str] = None
    district_name: Optional[str] = None
    subject_name: str
    level_name: str
    score: Decimal
    ranking: int
    prize: Optional[Decimal] = None


class StudentTranscriptItemResponse(BaseModel):
    evaluation_id: str
    academic_id: Optional[str] = None
    academic_year: Optional[str] = None
    semester: str
    evaluation_type: Optional[str] = None
    subject_name: str
    level_name: str
    score: Decimal
    ranking: int
    prize: Optional[Decimal] = None
