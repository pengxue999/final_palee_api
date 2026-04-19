from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime
from decimal import Decimal


def format_datetime(value):
    """Format datetime to DD-MM-YYYY HH:MM:SS string"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y %H:%M:%S")
    return value


class SalaryPaymentCreate(BaseModel):
    salary_payment_id: Optional[str] = None
    teacher_id: str
    user_id: int
    month: int
    total_amount: Decimal
    payment_date: datetime
    status: str


class SalaryPaymentUpdate(BaseModel):
    month: Optional[int] = None
    total_amount: Optional[Decimal] = None
    payment_date: Optional[datetime] = None
    status: Optional[str] = None


class SalaryPaymentResponse(BaseModel):
    salary_payment_id: str
    teacher_id: str
    teacher_name: str
    teacher_lastname: str
    user_name: str
    year: int
    month: int
    total_amount: Decimal
    payment_date: datetime
    status: str

    @classmethod
    def model_validate(cls, obj):
        return cls(
            salary_payment_id=obj.salary_payment_id,
            teacher_id=obj.teacher_id,
            teacher_name=obj.teacher.teacher_name,
            teacher_lastname=obj.teacher.teacher_lastname,
            user_name=obj.user.user_name,
            year=obj.payment_date.year,
            month=obj.month,
            total_amount=obj.total_amount,
            payment_date=obj.payment_date,
            status=obj.status,
        )

    model_config = {"from_attributes": True}

    @field_serializer('payment_date')
    def serialize_datetime(self, value):
        return format_datetime(value)


class SalaryPaymentReceiptRequest(BaseModel):
    salary_payment_id: str
    invoice_id: str
    teacher_id: str
    teacher_name: str
    user_name: str
    pay_date: datetime
    month: int
    month_label: str
    year: int
    installment_index: int
    installment_total: int
    total_hours: float
    hourly_rate: Decimal
    expected_amount: Decimal
    prior_debt: Decimal = Decimal('0')
    outstanding_before_payment: Decimal
    paid_amount: Decimal
    cumulative_paid_amount: Decimal
    remaining_amount: Decimal
    status: str

    @field_serializer('pay_date')
    def serialize_pay_date(self, value):
        return format_datetime(value)
