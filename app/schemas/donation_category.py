from typing import Optional

from pydantic import BaseModel, Field


class DonationCategoryBase(BaseModel):
    donation_category_name: str = Field(..., max_length=30)


class DonationCategoryCreate(DonationCategoryBase):
    pass


class DonationCategoryUpdate(BaseModel):
    donation_category_name: Optional[str] = Field(None, max_length=30)


class DonationCategoryResponse(DonationCategoryBase):
    donation_category_id: int

    class Config:
        from_attributes = True