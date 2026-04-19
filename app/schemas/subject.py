from pydantic import BaseModel
from typing import Optional


class SubjectCreate(BaseModel):
    subject_name: str
    subject_category_id: str

class SubjectUpdate(BaseModel):
    subject_name: Optional[str] = None
    subject_category_id: Optional[str] = None

class SubjectResponse(BaseModel):
    subject_id: str
    subject_name: str
    subject_category_name: str

    @classmethod
    def model_validate(cls, obj):
        return cls(
            subject_id=obj.subject_id,
            subject_name=obj.subject_name,
            subject_category_name=obj.category.subject_category_name
        )

    model_config = {"from_attributes": True}
