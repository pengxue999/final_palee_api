from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.district import DistrictCreate, DistrictUpdate, DistrictResponse
from app.configs.response import success_response
from app.services import district as svc

router = APIRouter(prefix="/districts", tags=["ເມືອງ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [DistrictResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນເມືອງທັງໝົດສຳເລັດ"
    )


@router.get("/province/{province_id}")
def get_districts_by_province(province_id: int, db: Session = Depends(get_db)):
    data = svc.get_by_province_id(db, province_id)
    return success_response(
        [DistrictResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນເມືອງຕາມແຂວງສຳເລັດ"
    )


@router.get("/{district_id}")
def get_one(district_id: int, db: Session = Depends(get_db)):
    return success_response(
        DistrictResponse.model_validate(svc.get_by_id(db, district_id)),
        "ດຶງຂໍ້ມູນເມືອງສຳເລັດ"
    )


@router.post("")
def create(data: DistrictCreate, db: Session = Depends(get_db)):
    return success_response(
        DistrictResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກເມືອງສຳເລັດ", 201
    )


@router.put("/{district_id}")
def update(district_id: int, data: DistrictUpdate, db: Session = Depends(get_db)):
    return success_response(
        DistrictResponse.model_validate(svc.update(db, district_id, data)),
        "ອັບເດດເມືອງສຳເລັດ"
    )


@router.delete("/{district_id}")
def delete(district_id: int, db: Session = Depends(get_db)):
    svc.delete(db, district_id)
    return success_response(None, "ລຶບເມືອງສຳເລັດ")
