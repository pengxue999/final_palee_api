from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.subject_category import SubjectCategoryCreate, SubjectCategoryUpdate, SubjectCategoryResponse
from app.configs.response import success_response
from app.services import subject_category as svc

router = APIRouter(prefix="/subject-categories", tags=["ໝວດວິຊາ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [SubjectCategoryResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນໝວດວິຊາທັງໝົດສຳເລັດ"
    )


@router.get("/{category_id}")
def get_one(category_id: str, db: Session = Depends(get_db)):
    return success_response(
        SubjectCategoryResponse.model_validate(svc.get_by_id(db, category_id)),
        "ດຶງຂໍ້ມູນໝວດວິຊາສຳເລັດ"
    )


@router.post("")
def create(data: SubjectCategoryCreate, db: Session = Depends(get_db)):
    return success_response(
        SubjectCategoryResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກໝວດວິຊາສຳເລັດ", 201
    )


@router.put("/{category_id}")
def update(category_id: str, data: SubjectCategoryUpdate, db: Session = Depends(get_db)):
    return success_response(
        SubjectCategoryResponse.model_validate(svc.update(db, category_id, data)),
        "ອັບເດດໝວດວິຊາສຳເລັດ"
    )


@router.delete("/{category_id}")
def delete(category_id: str, db: Session = Depends(get_db)):
    svc.delete(db, category_id)
    return success_response(None, "ລຶບໝວດວິຊາສຳເລັດ")
