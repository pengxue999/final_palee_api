from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.configs.response import success_response
from app.services import user as svc

router = APIRouter(prefix="/users", tags=["ຜູ້ໃຊ້"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [UserResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນຜູ້ໃຊ້ທັງໝົດສຳເລັດ"
    )


@router.get("/{user_id}")
def get_one(user_id: int, db: Session = Depends(get_db)):
    return success_response(
        UserResponse.model_validate(svc.get_by_id(db, user_id)),
        "ດຶງຂໍ້ມູນຜູ້ໃຊ້ສຳເລັດ"
    )


@router.post("")
def create(data: UserCreate, db: Session = Depends(get_db)):
    return success_response(
        UserResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກຜູ້ໃຊ້ສຳເລັດ", 201
    )


@router.put("/{user_id}")
def update(user_id: int, data: UserUpdate, db: Session = Depends(get_db)):
    return success_response(
        UserResponse.model_validate(svc.update(db, user_id, data)),
        "ອັບເດດຜູ້ໃຊ້ສຳເລັດ"
    )


@router.delete("/{user_id}")
def delete(user_id: int, db: Session = Depends(get_db)):
    svc.delete(db, user_id)
    return success_response(None, "ລຶບຜູ້ໃຊ້ສຳເລັດ")
