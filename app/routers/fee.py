from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.fee import FeeCreate, FeeUpdate, FeeResponse
from app.configs.response import success_response
from app.services import fee as svc

router = APIRouter(prefix="/fees", tags=["ຄ່າທຳນຽມ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [FeeResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນຄ່າທຳນຽມທັງໝົດສຳເລັດ"
    )


@router.get("/{fee_id}")
def get_one(fee_id: str, db: Session = Depends(get_db)):
    return success_response(
        FeeResponse.model_validate(svc.get_by_id(db, fee_id)),
        "ດຶງຂໍ້ມູນຄ່າທຳນຽມສຳເລັດ"
    )


@router.post("")
def create(data: FeeCreate, db: Session = Depends(get_db)):
    return success_response(
        FeeResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກຄ່າທຳນຽມສຳເລັດ", 201
    )


@router.put("/{fee_id}")
def update(fee_id: str, data: FeeUpdate, db: Session = Depends(get_db)):
    return success_response(
        FeeResponse.model_validate(svc.update(db, fee_id, data)),
        "ອັບເດດຄ່າທຳນຽມສຳເລັດ"
    )


@router.delete("/{fee_id}")
def delete(fee_id: str, db: Session = Depends(get_db)):
    svc.delete(db, fee_id)
    return success_response(None, "ລຶບຄ່າທຳນຽມສຳເລັດ")
