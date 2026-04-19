from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.donor import DonorCreate, DonorUpdate, DonorResponse
from app.configs.response import success_response
from app.services import donor as svc

router = APIRouter(prefix="/donors", tags=["ຜູ້ບໍລິຈາກ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [DonorResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນຜູ້ບໍລິຈາກທັງໝົດສຳເລັດ"
    )


@router.get("/{donor_id}")
def get_one(donor_id: str, db: Session = Depends(get_db)):
    return success_response(
        DonorResponse.model_validate(svc.get_by_id(db, donor_id)),
        "ດຶງຂໍ້ມູນຜູ້ບໍລິຈາກສຳເລັດ"
    )


@router.post("")
def create(data: DonorCreate, db: Session = Depends(get_db)):
    return success_response(
        DonorResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກຜູ້ບໍລິຈາກສຳເລັດ", 201
    )


@router.put("/{donor_id}")
def update(donor_id: str, data: DonorUpdate, db: Session = Depends(get_db)):
    return success_response(
        DonorResponse.model_validate(svc.update(db, donor_id, data)),
        "ອັບເດດຜູ້ບໍລິຈາກສຳເລັດ"
    )


@router.delete("/{donor_id}")
def delete(donor_id: str, db: Session = Depends(get_db)):
    svc.delete(db, donor_id)
    return success_response(None, "ລຶບຜູ້ບໍລິຈາກສຳເລັດ")
