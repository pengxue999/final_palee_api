from pydantic import BaseModel, Field
from typing import Optional

class UnitBase(BaseModel):
    unit_name: str = Field(..., max_length=30)

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    unit_name: Optional[str] = Field(None, max_length=30)

class UnitResponse(UnitBase):
    unit_id: int

    class Config:
        from_attributes = True
