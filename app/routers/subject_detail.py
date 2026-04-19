from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.configs.database import get_db
from app.configs.exceptions import ForeignKeyConstraintException
from app.models.subject_detail import SubjectDetail as SubjectDetailModel
from app.schemas.subject_detail import SubjectDetailCreate, SubjectDetailUpdate, SubjectDetailResponse
from app.configs.response import success_response, error_response
from app.services import subject_detail as svc

router = APIRouter(prefix="/subject-details", tags=["subject-details"])

@router.get("")
def get_all_subject_details(db: Session = Depends(get_db)):
    subject_details = svc.get_all(db)
    return success_response(
        [SubjectDetailResponse.model_validate(subject_detail) for subject_detail in subject_details],
        "ດຶງຂໍ້ມູນລາຍລະອຽດວິຊາທັງໝົດສຳເລັດ"
    )

@router.get("/{subject_detail_id}")
def get_subject_detail(subject_detail_id: str, db: Session = Depends(get_db)):
    try:
        subject_detail = svc.get_by_id(db, subject_detail_id)
        return success_response(
            SubjectDetailResponse.model_validate(subject_detail),
            "ດຶງຂໍ້ມູນລາຍລະອຽດວິຊາສຳເລັດ"
        )
    except Exception:
        return error_response("NOT_FOUND", "ບໍ່ພົບຂໍ້ມູນລາຍລະອຽດວິຊາ", 404)

@router.post("")
def create_subject_detail(subject_detail: SubjectDetailCreate, db: Session = Depends(get_db)):
    try:
        created_subject_detail = svc.create(db, subject_detail)
        return success_response(
            SubjectDetailResponse.model_validate(created_subject_detail),
            "ບັນທຶກລາຍລະອຽດວິຊາສຳເລັດ", 201
        )
    except Exception as e:
        if "ບໍ່ພົບຂໍ້ມູນ" in str(e):
            return error_response("NOT_FOUND", str(e), 404)
        return error_response("VALIDATION_ERROR", str(e), 400)

@router.put("/{subject_detail_id}")
def update_subject_detail(subject_detail_id: str, subject_detail: SubjectDetailUpdate, db: Session = Depends(get_db)):
    try:
        updated_subject_detail = svc.update(db, subject_detail_id, subject_detail)
        return success_response(
            SubjectDetailResponse.model_validate(updated_subject_detail),
            "ອັບເດດລາຍລະອຽດວິຊາສຳເລັດ"
        )
    except Exception:
        return error_response("NOT_FOUND", "ບໍ່ພົບຂໍ້ມູນລາຍລະອຽດວິຊາ", 404)

@router.delete("/{subject_detail_id}")
def delete_subject_detail(subject_detail_id: str, db: Session = Depends(get_db)):
    try:
        svc.delete(db, subject_detail_id)
        return success_response(None, "ລຶບລາຍລະອຽດວິຊາສຳເລັດ")
    except ForeignKeyConstraintException as e:
        return error_response("CONFLICT", str(e), 409)
    except Exception:
        return error_response("NOT_FOUND", "ບໍ່ພົບຂໍ້ມູນລາຍລະອຽດວິຊາ", 404)
