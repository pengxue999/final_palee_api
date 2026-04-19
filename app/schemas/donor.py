from pydantic import BaseModel
from typing import Optional


class DonorCreate(BaseModel):
    donor_name: str
    donor_lastname: str
    donor_contact: str
    section: Optional[str] = None


class DonorUpdate(BaseModel):
    donor_name: Optional[str] = None
    donor_lastname: Optional[str] = None
    donor_contact: Optional[str] = None
    section: Optional[str] = None


class DonorResponse(BaseModel):
    donor_id: str
    donor_name: str
    donor_lastname: str
    donor_contact: str
    section: Optional[str] = None

    model_config = {"from_attributes": True}
