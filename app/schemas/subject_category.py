from pydantic import BaseModel
from typing import Optional


class SubjectCategoryCreate(BaseModel):
    subject_category_name: str

class SubjectCategoryUpdate(BaseModel):
    subject_category_name: Optional[str] = None

class SubjectCategoryResponse(BaseModel):
    subject_category_id: str
    subject_category_name: str
    model_config = {"from_attributes": True}
