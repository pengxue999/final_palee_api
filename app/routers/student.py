from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.student import StudentCreate, StudentUpdate, StudentResponse
from app.configs.response import success_response
from app.services import student as svc

router = APIRouter(prefix="/students", tags=["ນັກຮຽນ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    students = svc.get_all(db)
    return success_response(
        [StudentResponse.model_validate(student) for student in students],
        "ດຶງຂໍ້ມູນນັກຮຽນທັງໝົດສຳເລັດ"
    )


@router.get("/{student_id}")
def get_one(student_id: str, db: Session = Depends(get_db)):
    student = svc.get_by_id(db, student_id)
    return success_response(
        StudentResponse.model_validate(student),
        "ດຶງຂໍ້ມູນນັກຮຽນສຳເລັດ"
    )


@router.post("")
def create(data: StudentCreate, db: Session = Depends(get_db)):
    student = svc.create(db, data)
    return success_response(
        StudentResponse.model_validate(student),
        "ບັນທຶກນັກຮຽນສຳເລັດ", 201
    )


@router.put("/{student_id}")
def update(student_id: str, data: StudentUpdate, db: Session = Depends(get_db)):
    student = svc.update(db, student_id, data)
    return success_response(
        StudentResponse.model_validate(student),
        "ອັບເດດນັກຮຽນສຳເລັດ"
    )


@router.delete("/{student_id}")
def delete(student_id: str, db: Session = Depends(get_db)):
    svc.delete(db, student_id)
    return success_response(None, "ລຶບນັກຮຽນສຳເລັດ")
