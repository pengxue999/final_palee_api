from pydantic import BaseModel
from typing import Optional


class ProvinceCreate(BaseModel):
    province_name: str

class ProvinceUpdate(BaseModel):
    province_name: Optional[str] = None

class ProvinceResponse(BaseModel):
    province_id: int
    province_name: str
    model_config = {"from_attributes": True}
