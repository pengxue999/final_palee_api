from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.teacher_assignment import TeacherAssignmentCreate, TeacherAssignmentUpdate, TeacherAssignmentResponse
from app.configs.response import success_response
from app.services import teacher_assignment as svc

router = APIRouter(prefix="/teacher-assignments", tags=["ການມອບໝາຍອາຈານ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [TeacherAssignmentResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນການມອບໝາຍອາຈານທັງໝົດສຳເລັດ"
    )


@router.get("/by-teacher/{teacher_id}")
def get_by_teacher(teacher_id: str, db: Session = Depends(get_db)):
    data = svc.get_by_teacher(db, teacher_id)
    return success_response(
        [TeacherAssignmentResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນການມອບໝາຍອາຈານສຳເລັດ"
    )


@router.get("/{assignment_id}")
def get_one(assignment_id: str, db: Session = Depends(get_db)):
    return success_response(
        TeacherAssignmentResponse.model_validate(svc.get_by_id(db, assignment_id)),
        "ດຶງຂໍ້ມູນການມອບໝາຍອາຈານສຳເລັດ"
    )


@router.post("")
def create(data: TeacherAssignmentCreate, db: Session = Depends(get_db)):
    return success_response(
        TeacherAssignmentResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກການມອບໝາຍອາຈານສຳເລັດ", 201
    )


@router.put("/{assignment_id}")
def update(assignment_id: str, data: TeacherAssignmentUpdate, db: Session = Depends(get_db)):
    return success_response(
        TeacherAssignmentResponse.model_validate(svc.update(db, assignment_id, data)),
        "ອັບເດດການມອບໝາຍອາຈານສຳເລັດ"
    )


@router.delete("/{assignment_id}")
def delete(assignment_id: str, db: Session = Depends(get_db)):
    svc.delete(db, assignment_id)
    return success_response(None, "ລຶບການມອບໝາຍອາຈານສຳເລັດ")
