from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import date
from decimal import Decimal
from app.utils.donation_category import normalize_donation_category_name


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
    donation_category: str
    donation_name: str
    amount: Decimal
    unit_id: int
    description: Optional[str] = None
    donation_date: date

class DonationUpdate(BaseModel):
    donor_id: Optional[str] = None
    donation_category: Optional[str] = None
    donation_name: Optional[str] = None
    amount: Optional[Decimal] = None
    unit_id: Optional[int] = None
    description: Optional[str] = None
    donation_date: Optional[date] = None

class DonationResponse(BaseModel):
    donation_id: int
    donor_id: str
    donor_name: str
    donor_lastname: str
    donation_category_name: str
    donation_name: str
    amount: Decimal
    unit_name: str
    description: Optional[str]
    donation_date: date

    @classmethod
    def model_validate(cls, obj):
        category_name = normalize_donation_category_name(obj.donation_category)
        return cls(
            donation_id=obj.donation_id,
            donor_id=obj.donor.donor_id,
            donor_name=obj.donor.donor_name,
            donor_lastname=obj.donor.donor_lastname,
            donation_category_name=category_name,
            donation_name=obj.donation_name,
            amount=obj.amount,
            unit_name=obj.unit.unit_name,
            description=obj.description,
            donation_date=obj.donation_date
        )

    model_config = {"from_attributes": True}

    @field_serializer('donation_date')
    def serialize_donation_date(self, value):
        return format_date(value)
