from pydantic import BaseModel
from typing import Optional


class DistrictCreate(BaseModel):
    district_name: str
    province_id: int

class DistrictUpdate(BaseModel):
    district_name: Optional[str] = None
    province_id: Optional[int] = None

class DistrictResponse(BaseModel):
    district_id: int
    district_name: str
    province_name: str

    @classmethod
    def model_validate(cls, obj):
        return cls(
            district_id=obj.district_id,
            district_name=obj.district_name,
            province_name=obj.province.province_name
        )

    model_config = {"from_attributes": True}
