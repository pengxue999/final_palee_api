from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.configs.response import success_response
from app.services import expense as svc

router = APIRouter(prefix="/expenses", tags=["ລາຍຈ່າຍ"])


@router.get("")
def get_expenses(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [ExpenseResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນລາຍຈ່າຍທັງໝົດສຳເລັດ"
    )


@router.get("/{expense_id}")
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    return success_response(
        ExpenseResponse.model_validate(svc.get_by_id(db, expense_id)),
        "ດຶງຂໍ້ມູນລາຍຈ່າຍສຳເລັດ"
    )


@router.post("")
def create_expense(data: ExpenseCreate, db: Session = Depends(get_db)):
    return success_response(
        ExpenseResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກລາຍຈ່າຍສຳເລັດ", 201
    )


@router.put("/{expense_id}")
def update_expense(expense_id: int, data: ExpenseUpdate, db: Session = Depends(get_db)):
    return success_response(
        ExpenseResponse.model_validate(svc.update(db, expense_id, data)),
        "ອັບເດດລາຍຈ່າຍສຳເລັດ"
    )


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    svc.delete(db, expense_id)
    return success_response(None, "ລຶບລາຍຈ່າຍສຳເລັດ")
