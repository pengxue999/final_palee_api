from pydantic import BaseModel
from typing import Optional
from decimal import Decimal
from app.enums.scholarship import ScholarshipEnum


class RegistrationDetailCreate(BaseModel):
    registration_id: str
    fee_id: str
    scholarship: ScholarshipEnum


class RegistrationDetailUpdate(BaseModel):
    registration_id: Optional[str] = None
    fee_id: Optional[str] = None
    scholarship: Optional[ScholarshipEnum] = None


class RegistrationDetailResponse(BaseModel):
    regis_detail_id: int
    registration_id: str
    fee_id: str
    scholarship: ScholarshipEnum

    model_config = {"from_attributes": True}
