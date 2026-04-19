from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.academic_years import AcademicYearCreate, AcademicYearUpdate, AcademicYearResponse
from app.configs.response import success_response
from app.services import academic_years as svc

router = APIRouter(prefix="/academic-years", tags=["ສົກຮຽນ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [AcademicYearResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນສົກຮຽນທັງໝົດສຳເລັດ"
    )


@router.get("/{year_id}")
def get_one(year_id: str, db: Session = Depends(get_db)):
    return success_response(
        AcademicYearResponse.model_validate(svc.get_by_id(db, year_id)),
        "ດຶງຂໍ້ມູນສົກຮຽນສຳເລັດ"
    )


@router.post("")
def create(data: AcademicYearCreate, db: Session = Depends(get_db)):
    return success_response(
        AcademicYearResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກສົກຮຽນສຳເລັດ", 201
    )


@router.put("/{year_id}")
def update(year_id: str, data: AcademicYearUpdate, db: Session = Depends(get_db)):
    return success_response(
        AcademicYearResponse.model_validate(svc.update(db, year_id, data)),
        "ອັບເດດສົກຮຽນສຳເລັດ"
    )


@router.delete("/{year_id}")
def delete(year_id: str, db: Session = Depends(get_db)):
    svc.delete(db, year_id)
    return success_response(None, "ລຶບສົກຮຽນສຳເລັດ")
