from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.discount import DiscountCreate, DiscountUpdate
from app.configs.response import success_response
from app.services import discount as svc

router = APIRouter(prefix="/discounts", tags=["ສ່ວນຫຼຸດ"])


from app.schemas.discount import DiscountCreate, DiscountUpdate, DiscountResponse

@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [DiscountResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນສ່ວນຫຼຸດທັງໝົດສຳເລັດ"
    )

@router.get("/{discount_id}")
def get_one(discount_id: str, db: Session = Depends(get_db)):
    return success_response(
        DiscountResponse.model_validate(svc.get_by_id(db, discount_id)),
        "ດຶງຂໍ້ມູນສ່ວນຫຼຸດສຳເລັດ"
    )

@router.post("")
def create(data: DiscountCreate, db: Session = Depends(get_db)):
    return success_response(
        DiscountResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກສ່ວນຫຼຸດສຳເລັດ", 201
    )

@router.put("/{discount_id}")
def update(discount_id: str, data: DiscountUpdate, db: Session = Depends(get_db)):
    return success_response(
        DiscountResponse.model_validate(svc.update(db, discount_id, data)),
        "ອັບເດດສ່ວນຫຼຸດສຳເລັດ"
    )


@router.delete("/{discount_id}")
def delete(discount_id: str, db: Session = Depends(get_db)):
    svc.delete(db, discount_id)
    return success_response(None, "ລຶບສ່ວນຫຼຸດສຳເລັດ")
