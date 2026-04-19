from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.level import LevelCreate, LevelUpdate, LevelResponse
from app.configs.response import success_response
from app.services import level as svc

router = APIRouter(prefix="/levels", tags=["ລະດັບ/ຊັ້ນຮຽນ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [LevelResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນຂັ້ນຊັ້ນທັງໝົດສຳເລັດ"
    )


@router.get("/{level_id}")
def get_one(level_id: str, db: Session = Depends(get_db)):
    return success_response(
        LevelResponse.model_validate(svc.get_by_id(db, level_id)),
        "ດຶງຂໍ້ມູນຂັ້ນຊັ້ນສຳເລັດ"
    )


@router.post("")
def create(data: LevelCreate, db: Session = Depends(get_db)):
    return success_response(
        LevelResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກຂັ້ນຊັ້ນສຳເລັດ", 201
    )


@router.put("/{level_id}")
def update(level_id: str, data: LevelUpdate, db: Session = Depends(get_db)):
    return success_response(
        LevelResponse.model_validate(svc.update(db, level_id, data)),
        "ອັບເດດຂັ້ນຊັ້ນສຳເລັດ"
    )


@router.delete("/{level_id}")
def delete(level_id: str, db: Session = Depends(get_db)):
    svc.delete(db, level_id)
    return success_response(None, "ລຶບຂັ້ນຊັ້ນສຳເລັດ")
