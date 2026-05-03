from pydantic import BaseModel, field_serializer
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from app.enums.registration_status import RegistrationStatusEnum


def format_date(value):
    """Format datetime to YYYY-MM-DD string"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y %H:%M:%S")
    return value


class RegistrationDetailItem(BaseModel):
    """Registration detail item for bulk creation"""
    fee_id: str
    scholarship: str


class RegistrationBulkCreate(BaseModel):
    """Bulk create registration with details in one request"""
    registration_id: Optional[str] = None
    student_id: str
    discount_id: Optional[str] = None
    total_amount: Decimal
    final_amount: Decimal
    status: RegistrationStatusEnum
    registration_date: datetime
    details: List[RegistrationDetailItem]


class RegistrationReceiptFeeItem(BaseModel):
    subject_name: str
    level_name: str
    fee: Decimal


class RegistrationReceiptRequest(BaseModel):
    registration_id: str
    registration_date: datetime
    student_name: str
    selected_fees: List[RegistrationReceiptFeeItem]
    tuition_fee: Decimal
    total_fee: Decimal
    discount_amount: Decimal
    net_fee: Decimal


class RegistrationCreate(BaseModel):
    registration_id: str
    student_id: str
    discount_id: Optional[str] = None
    total_amount: Decimal
    final_amount: Decimal
    status: RegistrationStatusEnum
    registration_date: datetime

class RegistrationUpdate(BaseModel):
    student_id: Optional[str] = None
    discount_id: Optional[str] = None
    total_amount: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    status: Optional[RegistrationStatusEnum] = None
    registration_date: Optional[datetime] = None

class RegistrationResponse(BaseModel):
    registration_id: str
    student_name: str
    student_lastname: str
    academic_id: Optional[str] = None
    academic_year: Optional[str] = None
    discount_description: Optional[str]
    total_amount: Decimal
    final_amount: Decimal
    paid_amount: Decimal
    status: RegistrationStatusEnum
    registration_date: datetime

    @classmethod
    def model_validate(cls, obj, paid_amount: Decimal = Decimal('0')):
        status_value = obj.status
        if hasattr(status_value, 'value'):
            status_value = status_value.value
        elif status_value == '' or status_value is None:
            status_value = RegistrationStatusEnum.UNPAID.value

        academic_id = None
        academic_year = None

        for detail in obj.details or []:
            fee = getattr(detail, 'fee_rel', None)
            year = getattr(fee, 'academic_year', None)
            if year is not None:
                academic_id = year.academic_id
                academic_year = year.academic_year
                break

        if academic_year is None and obj.discount is not None:
            discount_year = getattr(obj.discount, 'academic_year', None)
            if discount_year is not None:
                academic_id = discount_year.academic_id
                academic_year = discount_year.academic_year

        return cls(
            registration_id=obj.registration_id,
            student_name=obj.student.student_name,
            student_lastname=obj.student.student_lastname,
            academic_id=academic_id,
            academic_year=academic_year,
            discount_description=obj.discount.discount_description if obj.discount else None,
            total_amount=obj.total_amount,
            final_amount=obj.final_amount,
            paid_amount=paid_amount,
            status=status_value,
            registration_date=obj.registration_date
        )

    model_config = {"from_attributes": True}

    @field_serializer('registration_date')
    def serialize_registration_date(self, value):
        return format_date(value)


class RegistrationDetailCreate(BaseModel):
    registration_id: Optional[str] = None
    fee_id: str
    scholarship: str

class RegistrationDetailUpdate(BaseModel):
    registration_id: Optional[str] = None
    fee_id: Optional[str] = None
    scholarship: Optional[str] = None

class RegistrationDetailResponse(BaseModel):
    regis_detail_id: int
    registration_id: str
    subject_name: str
    level_name: str
    scholarship: str

    @classmethod
    def model_validate(cls, obj):
        return cls(
            regis_detail_id=obj.regis_detail_id,
            registration_id=obj.registration_id,
            subject_name=obj.fee_rel.subject.subject_name,
            level_name=obj.fee_rel.level.level_name,
            scholarship=obj.scholarship.value if obj.scholarship else None
        )

    model_config = {"from_attributes": True}
