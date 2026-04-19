from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


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
    prize: Optional[Decimal] = None

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
            prize=obj.prize,
        )

    model_config = {"from_attributes": True}
