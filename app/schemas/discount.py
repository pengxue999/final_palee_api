from pydantic import BaseModel, field_serializer
from typing import Optional

from decimal import Decimal

class DiscountCreate(BaseModel):
    academic_id: str
    discount_amount: Decimal
    discount_description: str

class DiscountUpdate(BaseModel):
    academic_id: Optional[str] = None
    discount_amount: Optional[Decimal] = None
    discount_description: Optional[str] = None

class DiscountResponse(BaseModel):
    discount_id: str
    discount_amount: Decimal
    discount_description: str
    academic_year: Optional[str]

    @classmethod
    def model_validate(cls, obj):
        desc_val = str(obj.discount_description)
        return cls(
            discount_id=obj.discount_id,
            discount_amount=obj.discount_amount,
            discount_description=desc_val,
            academic_year=obj.academic_year.academic_year if obj.academic_year else None
        )
