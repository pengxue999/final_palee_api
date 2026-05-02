import re
from pydantic import BaseModel, field_validator
from typing import Optional


_VALID_GENDERS = {"MALE", "FEMALE"}

class StudentCreate(BaseModel):
    student_name: str
    student_lastname: str
    gender: str
    student_contact: str
    parents_contact: str
    school: str
    district_id: int

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v not in _VALID_GENDERS:
            raise ValueError("gender must be 'MALE' or 'FEMALE'")
        return v

    @field_validator('student_contact', 'parents_contact')
    @classmethod
    def validate_phone(cls, v):
        if v.startswith('020') and re.match(r'^020\d{8}$', v):
            return v
        if v.startswith('030') and re.match(r'^030\d{7}$', v):
            return v
        raise ValueError("ເບີໂທຕ້ອງຢູ່ໃນຮູບແບບ 020XXXXXXXX ຫຼື 030XXXXXXX")

class StudentUpdate(BaseModel):
    student_name: Optional[str] = None
    student_lastname: Optional[str] = None
    gender: Optional[str] = None
    student_contact: Optional[str] = None
    parents_contact: Optional[str] = None
    school: Optional[str] = None
    district_id: Optional[int] = None

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in _VALID_GENDERS:
            raise ValueError("gender must be 'MALE' or 'FEMALE'")
        return v

    @field_validator('student_contact', 'parents_contact')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        if v.startswith('020') and re.match(r'^020\d{8}$', v):
            return v
        if v.startswith('030') and re.match(r'^030\d{7}$', v):
            return v
        raise ValueError("ເບີໂທຕ້ອງຢູ່ໃນຮູບແບບ 020XXXXXXXX ຫຼື 030XXXXXXX")

class StudentResponse(BaseModel):
    student_id: str
    student_name: str
    student_lastname: str
    gender: str
    student_contact: str
    parents_contact: str
    school: str
    district_name: str
    province_name: str

    @classmethod
    def model_validate(cls, obj):
        return cls(
            student_id=obj.student_id,
            student_name=obj.student_name,
            student_lastname=obj.student_lastname,
            gender=obj.gender,
            student_contact=obj.student_contact,
            parents_contact=obj.parents_contact,
            school=obj.school,
            district_name=obj.district.district_name,
            province_name=obj.district.province.province_name,
        )

    model_config = {"from_attributes": True}
