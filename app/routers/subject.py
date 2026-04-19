from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.configs.response import success_response
from app.services import subject as svc

router = APIRouter(prefix="/subjects", tags=["ວິຊາ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [SubjectResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນວິຊາທັງໝົດສຳເລັດ"
    )


@router.get("/{subject_id}")
def get_one(subject_id: str, db: Session = Depends(get_db)):
    return success_response(
        SubjectResponse.model_validate(svc.get_by_id(db, subject_id)),
        "ດຶງຂໍ້ມູນວິຊາສຳເລັດ"
    )


@router.post("")
def create(data: SubjectCreate, db: Session = Depends(get_db)):
    return success_response(
        SubjectResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກວິຊາສຳເລັດ", 201
    )


@router.put("/{subject_id}")
def update(subject_id: str, data: SubjectUpdate, db: Session = Depends(get_db)):
    return success_response(
        SubjectResponse.model_validate(svc.update(db, subject_id, data)),
        "ອັບເດດວິຊາສຳເລັດ"
    )


@router.delete("/{subject_id}")
def delete(subject_id: str, db: Session = Depends(get_db)):
    svc.delete(db, subject_id)
    return success_response(None, "ລຶບວິຊາສຳເລັດ")
