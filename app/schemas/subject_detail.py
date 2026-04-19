from pydantic import BaseModel, Field
from typing import Optional


class SubjectDetailCreate(BaseModel):
    subject_id: str = Field(..., max_length=5)
    level_id: str = Field(..., max_length=5)


class SubjectDetailUpdate(BaseModel):
    subject_id: Optional[str] = Field(None, max_length=5)
    level_id: Optional[str] = Field(None, max_length=5)


class SubjectDetailResponse(BaseModel):
    subject_detail_id: str
    subject_id: str
    level_id: str
    subject_name: str
    level_name: str

    @classmethod
    def model_validate(cls, obj):
        return cls(
            subject_detail_id=obj.subject_detail_id,
            subject_id=obj.subject_id,
            level_id=obj.level_id,
            subject_name=obj.subject.subject_name,
            level_name=obj.level.level_name,
        )

    model_config = {"from_attributes": True}
