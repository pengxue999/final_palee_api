from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.income import IncomeCreate, IncomeUpdate, IncomeResponse
from app.configs.response import success_response
from app.services import income as svc

router = APIRouter(prefix="/incomes", tags=["ລາຍຮັບ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [IncomeResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນລາຍຮັບທັງໝົດສຳເລັດ"
    )


@router.get("/{income_id}")
def get_one(income_id: int, db: Session = Depends(get_db)):
    return success_response(
        IncomeResponse.model_validate(svc.get_by_id(db, income_id)),
        "ດຶງຂໍ້ມູນລາຍຮັບສຳເລັດ"
    )


@router.post("")
def create(data: IncomeCreate, db: Session = Depends(get_db)):
    return success_response(
        IncomeResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກລາຍຮັບສຳເລັດ", 201
    )


@router.put("/{income_id}")
def update(income_id: int, data: IncomeUpdate, db: Session = Depends(get_db)):
    return success_response(
        IncomeResponse.model_validate(svc.update(db, income_id, data)),
        "ອັບເດດລາຍຮັບສຳເລັດ"
    )


@router.delete("/{income_id}")
def delete(income_id: int, db: Session = Depends(get_db)):
    svc.delete(db, income_id)
    return success_response(None, "ລຶບລາຍຮັບສຳເລັດ")
