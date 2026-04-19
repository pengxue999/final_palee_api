from pydantic import BaseModel
from typing import Optional


class ExpenseCategoryCreate(BaseModel):
    expense_category: str


class ExpenseCategoryUpdate(BaseModel):
    expense_category: Optional[str] = None


class ExpenseCategoryResponse(BaseModel):
    expense_category_id: int
    expense_category: str
    model_config = {"from_attributes": True}
