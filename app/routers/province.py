from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.province import ProvinceCreate, ProvinceUpdate, ProvinceResponse
from app.configs.response import success_response
from app.services import province as svc

router = APIRouter(prefix="/provinces", tags=["ແຂວງ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [ProvinceResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນແຂວງທັງໝົດສຳເລັດ"
    )


@router.get("/{province_id}")
def get_one(province_id: int, db: Session = Depends(get_db)):
    return success_response(
        ProvinceResponse.model_validate(svc.get_by_id(db, province_id)),
        "ດຶງຂໍ້ມູນແຂວງສຳເລັດ"
    )


@router.post("")
def create(data: ProvinceCreate, db: Session = Depends(get_db)):
    return success_response(
        ProvinceResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກແຂວງສຳເລັດ", 201
    )


@router.put("/{province_id}")
def update(province_id: int, data: ProvinceUpdate, db: Session = Depends(get_db)):
    return success_response(
        ProvinceResponse.model_validate(svc.update(db, province_id, data)),
        "ອັບເດດແຂວງສຳເລັດ"
    )


@router.delete("/{province_id}")
def delete(province_id: int, db: Session = Depends(get_db)):
    svc.delete(db, province_id)
    return success_response(None, "ລຶບແຂວງສຳເລັດ")
