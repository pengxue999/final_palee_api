from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.teaching_log import TeachingLogCreate, TeachingLogUpdate, TeachingLogResponse
from app.configs.response import success_response
from app.services import teaching_log as svc

router = APIRouter(prefix="/teaching-logs", tags=["ບົດບັນທຶກການສອນ"])


@router.get("")
def get_all(
    academic_year: str = None,
    month: str = None,
    status: str = None,
    teacher_id: str = None,
    db: Session = Depends(get_db)
):
    data = svc.get_all(
        db,
        academic_year=academic_year,
        month=month,
        status=status,
        teacher_id=teacher_id
    )
    return success_response(
        [TeachingLogResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນບົດບັນທຶກການສອນທັງໝົດສຳເລັດ"
    )


@router.get("/by-teacher/{teacher_id}")
def get_by_teacher(teacher_id: str, academic_year: str = None, from_date: str = None, to_date: str = None, db: Session = Depends(get_db)):
    data = svc.get_by_teacher(db, teacher_id, academic_year=academic_year, from_date=from_date, to_date=to_date)
    return success_response(
        [TeachingLogResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນບັນທຶກການສອນສຳເລັດ"
    )


@router.get("/summary")
def get_summary(academic_year: str = None, db: Session = Depends(get_db)):
    data = svc.get_summary(db, academic_year=academic_year)
    return success_response(data, "ດຶງຂໍ້ມູນສະຫຼຸບສຳເລັດ")


@router.get("/by-teacher/{teacher_id}/summary")
def get_summary_by_teacher(teacher_id: str, academic_year: str = None, db: Session = Depends(get_db)):
    data = svc.get_summary(db, teacher_id=teacher_id, academic_year=academic_year)
    return success_response(data, "ດຶງຂໍ້ມູນສະຫຼຸບສຳເລັດ")


@router.get("/{teaching_log_id}")
def get_one(teaching_log_id: int, db: Session = Depends(get_db)):
    return success_response(
        TeachingLogResponse.model_validate(svc.get_by_id(db, teaching_log_id)),
        "ດຶງຂໍ້ມູນບົດບັນທຶກການສອນສຳເລັດ"
    )


@router.post("")
def create(data: TeachingLogCreate, db: Session = Depends(get_db)):
    return success_response(
        TeachingLogResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກບົດບັນທຶກການສອນສຳເລັດ", 201
    )


@router.put("/{teaching_log_id}")
def update(teaching_log_id: int, data: TeachingLogUpdate, db: Session = Depends(get_db)):
    return success_response(
        TeachingLogResponse.model_validate(svc.update(db, teaching_log_id, data)),
        "ອັບເດດບົດບັນທຶກການສອນສຳເລັດ"
    )


@router.delete("/{teaching_log_id}")
def delete(teaching_log_id: int, db: Session = Depends(get_db)):
    svc.delete(db, teaching_log_id)
    return success_response(None, "ລຶບບົດບັນທຶກການສອນສຳເລັດ")
