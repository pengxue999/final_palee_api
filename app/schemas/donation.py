from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, field_serializer


def format_date(value):
    """Format date to YYYY-MM-DD string"""
    if value is None:
        return None
    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")
    return value


class DonorCreate(BaseModel):
    donor_id: str
    donor_name: str
    donor_lastname: str
    donor_contact: str
    description: Optional[str] = None

class DonorUpdate(BaseModel):
    donor_name: Optional[str] = None
    donor_lastname: Optional[str] = None
    donor_contact: Optional[str] = None
    description: Optional[str] = None

class DonorResponse(BaseModel):
    donor_id: str
    donor_name: str
    donor_lastname: str
    donor_contact: str
    description: Optional[str]
    model_config = {"from_attributes": True}


class DonationCreate(BaseModel):
    donor_id: str
    donation_category_id: int
    donation_name: str
    amount: Decimal
    unit: str
    donation_date: date

class DonationUpdate(BaseModel):
    donor_id: Optional[str] = None
    donation_category_id: Optional[int] = None
    donation_name: Optional[str] = None
    amount: Optional[Decimal] = None
    unit: Optional[str] = None
    donation_date: Optional[date] = None

class DonationResponse(BaseModel):
    donation_id: int
    donor_id: str
    donor_name: str
    donor_lastname: str
    donation_category_id: int
    donation_category_name: str
    donation_name: str
    amount: Decimal
    unit: str
    donation_date: date

    @classmethod
    def model_validate(cls, obj):
        category_name = (
            obj.donation_category.donation_category_name
            if obj.donation_category is not None
            else ""
        )
        return cls(
            donation_id=obj.donation_id,
            donor_id=obj.donor.donor_id,
            donor_name=obj.donor.donor_name,
            donor_lastname=obj.donor.donor_lastname,
            donation_category_id=obj.donation_category_id,
            donation_category_name=category_name,
            donation_name=obj.donation_name,
            amount=obj.amount,
            unit=obj.unit,
            donation_date=obj.donation_date
        )

    model_config = {"from_attributes": True}

    @field_serializer('donation_date')
    def serialize_donation_date(self, value):
        return format_date(value)
