from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import date, datetime
from decimal import Decimal


def format_date(value):
    """Format date/datetime to DD-MM-YYYY string"""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%d-%m-%Y")
    if isinstance(value, date):
        return value.strftime("%d-%m-%Y")
    return value


class ExpenseCreate(BaseModel):
    expense_category_id: int
    salary_payment_id: Optional[str] = None
    amount: Decimal
    description: Optional[str] = None
    expense_date: Optional[datetime] = None


class ExpenseUpdate(BaseModel):
    expense_category_id: Optional[int] = None
    salary_payment_id: Optional[str] = None
    amount: Optional[Decimal] = None
    description: Optional[str] = None
    expense_date: Optional[datetime] = None


class ExpenseResponse(BaseModel):
    expense_id: int
    expense_category_id: int
    expense_category: str
    salary_payment_id: Optional[str]
    amount: Decimal
    description: Optional[str]
    expense_date: datetime

    @classmethod
    def model_validate(cls, obj):
        return cls(
            expense_id=obj.expense_id,
            expense_category_id=obj.expense_category_id,
            expense_category=obj.category.expense_category,
            salary_payment_id=obj.salary_payment_id,
            amount=obj.amount,
            description=obj.description,
            expense_date=obj.expense_date,
        )

    model_config = {"from_attributes": True}

    @field_serializer('expense_date')
    def serialize_expense_date(self, value):
        return format_date(value)
