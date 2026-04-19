from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.expense_category import ExpenseCategoryCreate, ExpenseCategoryUpdate, ExpenseCategoryResponse
from app.configs.response import success_response
from app.services import expense_category as svc

router = APIRouter(prefix="/expense-categories", tags=["ປະເພດລາຍຈ່າຍ"])


@router.get("")
def get_categories(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [ExpenseCategoryResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນປະເພດລາຍຈ່າຍທັງໝົດສຳເລັດ"
    )


@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db)):
    return success_response(
        ExpenseCategoryResponse.model_validate(svc.get_by_id(db, category_id)),
        "ດຶງຂໍ້ມູນປະເພດລາຍຈ່າຍສຳເລັດ"
    )


@router.post("")
def create_category(data: ExpenseCategoryCreate, db: Session = Depends(get_db)):
    return success_response(
        ExpenseCategoryResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກປະເພດລາຍຈ່າຍສຳເລັດ", 201
    )


@router.put("/{category_id}")
def update_category(category_id: int, data: ExpenseCategoryUpdate, db: Session = Depends(get_db)):
    return success_response(
        ExpenseCategoryResponse.model_validate(svc.update(db, category_id, data)),
        "ອັບເດດປະເພດລາຍຈ່າຍສຳເລັດ"
    )


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    svc.delete(db, category_id)
    return success_response(None, "ລຶບປະເພດລາຍຈ່າຍສຳເລັດ")
