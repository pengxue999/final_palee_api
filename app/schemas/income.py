from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime
from decimal import Decimal


def format_date(value):
    """Format date to YYYY-MM-DD string"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")
    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")
    return value


class IncomeCreate(BaseModel):
    tuition_payment_id: Optional[str] = None
    donation_id: Optional[int] = None
    amount: Decimal
    description: Optional[str] = None
    income_date: Optional[datetime] = None


class IncomeUpdate(BaseModel):
    tuition_payment_id: Optional[str] = None
    donation_id: Optional[int] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    income_date: Optional[datetime] = None


class IncomeResponse(BaseModel):
    income_id: int
    tuition_payment_id: Optional[str]
    donation_id: Optional[int]
    amount: Decimal
    description: Optional[str]
    income_date: datetime
    model_config = {"from_attributes": True}

    @field_serializer('income_date')
    def serialize_income_date(self, value):
        return format_date(value)
