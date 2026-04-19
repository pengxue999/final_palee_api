import re
from pydantic import BaseModel, field_validator
from typing import Optional


class TeacherCreate(BaseModel):
    teacher_name: str
    teacher_lastname: str
    gender: str
    teacher_contact: str
    district_id: int

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v not in ["ຊາຍ", "ຍິງ"]:
            raise ValueError("ຕ້ອງເລືອກເພດກ່ອນ 'ຊາຍ' ຫຼື 'ຍິງ'")
        return v

    @field_validator('teacher_contact')
    @classmethod
    def validate_phone(cls, v):
        if v.startswith('020') and re.match(r'^020\d{8}$', v):
            return v
        if v.startswith('030') and re.match(r'^030\d{7}$', v):
            return v
        raise ValueError("ເບີໂທຕ້ອງຢູ່ໃນຮູບແບບ 020XXXXXXXX ຫຼື 030XXXXXXX")

class TeacherUpdate(BaseModel):
    teacher_name: Optional[str] = None
    teacher_lastname: Optional[str] = None
    gender: Optional[str] = None
    teacher_contact: Optional[str] = None
    district_id: Optional[int] = None

    @field_validator('gender')
    @classmethod
    def validate_gender(cls, v):
        if v is not None and v not in ["ຊາຍ", "ຍິງ"]:
            raise ValueError("ຕ້ອງເລືອກເພດກ່ອນ 'ຊາຍ' ຫຼື 'ຍິງ'")
        return v

    @field_validator('teacher_contact')
    @classmethod
    def validate_phone(cls, v):
        if v is None:
            return v
        if v.startswith('020') and re.match(r'^020\d{8}$', v):
            return v
        if v.startswith('030') and re.match(r'^030\d{7}$', v):
            return v
        raise ValueError("ເບີໂທຕ້ອງຢູ່ໃນຮູບແບບ 020XXXXXXXX ຫຼື 030XXXXXXX")

class TeacherResponse(BaseModel):
    teacher_id: str
    teacher_name: str
    teacher_lastname: str
    gender: str
    teacher_contact: str
    district_name: str
    province_name: str

    @classmethod
    def model_validate(cls, obj):
        return cls(
            teacher_id=obj.teacher_id,
            teacher_name=obj.teacher_name,
            teacher_lastname=obj.teacher_lastname,
            gender=obj.gender,
            teacher_contact=obj.teacher_contact,
            district_name=obj.district.district_name,
            province_name=obj.district.province.province_name
        )

    model_config = {"from_attributes": True}
