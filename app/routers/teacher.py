from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.teacher import TeacherCreate, TeacherUpdate, TeacherResponse
from app.configs.response import success_response
from app.services import teacher as svc

router = APIRouter(prefix="/teachers", tags=["ອາຈານ"])


@router.get("")
def get_teachers(db: Session = Depends(get_db)):
    data = svc.get_all_teachers(db)
    return success_response(
        [TeacherResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນອາຈານທັງໝົດສຳເລັດ"
    )


@router.get("/{teacher_id}")
def get_teacher(teacher_id: str, db: Session = Depends(get_db)):
    return success_response(
        TeacherResponse.model_validate(svc.get_teacher(db, teacher_id)),
        "ດຶງຂໍ້ມູນອາຈານສຳເລັດ"
    )


@router.post("")
def create_teacher(data: TeacherCreate, db: Session = Depends(get_db)):
    return success_response(
        TeacherResponse.model_validate(svc.create_teacher(db, data)),
        "ບັນທຶກອາຈານສຳເລັດ", 201
    )


@router.put("/{teacher_id}")
def update_teacher(teacher_id: str, data: TeacherUpdate, db: Session = Depends(get_db)):
    return success_response(
        TeacherResponse.model_validate(svc.update_teacher(db, teacher_id, data)),
        "ອັບເດດອາຈານສຳເລັດ"
    )


@router.delete("/{teacher_id}")
def delete_teacher(teacher_id: str, db: Session = Depends(get_db)):
    svc.delete_teacher(db, teacher_id)
    return success_response(None, "ລຶບອາຈານສຳເລັດ")
