from pydantic import BaseModel
from typing import Optional


class LevelCreate(BaseModel):
    level_name: str

class LevelUpdate(BaseModel):
    level_name: Optional[str] = None

class LevelResponse(BaseModel):
    level_id: str
    level_name: str
    model_config = {"from_attributes": True}
