from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class FeeCreate(BaseModel):
    subject_detail_id: str
    academic_id: str
    fee: Decimal

class FeeUpdate(BaseModel):
    subject_detail_id: Optional[str] = None
    academic_id: Optional[str] = None
    fee: Optional[Decimal] = None

class FeeResponse(BaseModel):
    fee_id: str
    subject_name: str
    level_name: str
    subject_category: str
    academic_year: str
    fee: Decimal

    @classmethod
    def model_validate(cls, obj):
        return cls(
            fee_id=obj.fee_id,
            subject_name=obj.subject_detail.subject.subject_name,
            level_name=obj.subject_detail.level.level_name,
            subject_category=obj.subject_detail.subject.category.subject_category_name,
            academic_year=obj.academic_year.academic_year,
            fee=obj.fee
        )

    model_config = {"from_attributes": True}
