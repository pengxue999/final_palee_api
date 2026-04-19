from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import date


def format_date(value):
    """Format date to YYYY-MM-DD string"""
    if value is None:
        return None
    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")
    return value


class AcademicYearCreate(BaseModel):
    academic_year: str
    start_date_at: date
    end_date_at: date
    status: str

class AcademicYearUpdate(BaseModel):
    academic_year: Optional[str] = None
    start_date_at: Optional[date] = None
    end_date_at: Optional[date] = None
    status: Optional[str] = None

class AcademicYearResponse(BaseModel):
    academic_id: str
    academic_year: str
    start_date_at: date
    end_date_at: date
    status: str
    model_config = {"from_attributes": True}

    @field_serializer('start_date_at', 'end_date_at')
    def serialize_dates(self, value):
        return format_date(value)
