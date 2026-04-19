from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.registration_detail import RegistrationDetailCreate, RegistrationDetailUpdate, RegistrationDetailResponse
from app.configs.response import success_response
from app.services import registration_detail as svc

router = APIRouter(prefix="/registration-details", tags=["ລາຍລະອຽດການລົງທະບຽນ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [RegistrationDetailResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນລາຍລະອຽດການລົງທະບຽນທັງໝົດສຳເລັດ"
    )


@router.get("/{regis_detail_id}")
def get_one(regis_detail_id: int, db: Session = Depends(get_db)):
    return success_response(
        RegistrationDetailResponse.model_validate(svc.get_by_id(db, regis_detail_id)),
        "ດຶງຂໍ້ມູນລາຍລະອຽດການລົງທະບຽນສຳເລັດ"
    )


@router.post("")
def create(data: RegistrationDetailCreate, db: Session = Depends(get_db)):
    return success_response(
        RegistrationDetailResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກລາຍລະອຽດການລົງທະບຽນສຳເລັດ", 201
    )


@router.put("/{regis_detail_id}")
def update(regis_detail_id: int, data: RegistrationDetailUpdate, db: Session = Depends(get_db)):
    return success_response(
        RegistrationDetailResponse.model_validate(svc.update(db, regis_detail_id, data)),
        "ອັບເດດລາຍລະອຽດການລົງທະບຽນສຳເລັດ"
    )


@router.delete("/{regis_detail_id}")
def delete(regis_detail_id: int, db: Session = Depends(get_db)):
    svc.delete(db, regis_detail_id)
    return success_response(None, "ລຶບລາຍລະອຽດການລົງທະບຽນສຳເລັດ")
