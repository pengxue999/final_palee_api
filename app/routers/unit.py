from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.configs.database import get_db
from app.models.unit import Unit as UnitModel
from app.schemas.unit import UnitCreate, UnitUpdate, UnitResponse
from app.configs.response import success_response, error_response
from app.services import unit as svc

router = APIRouter(prefix="/units", tags=["units"])

@router.get("")
def get_all_units(db: Session = Depends(get_db)):
    units = svc.get_all(db)
    return success_response(
        [UnitResponse.model_validate(unit) for unit in units],
        "ດຶງຂໍ້ມູນຫົວໜ່ວຍທັງໝົດສຳເລັດ"
    )

@router.get("/{unit_id}")
def get_unit(unit_id: int, db: Session = Depends(get_db)):
    try:
        unit = svc.get_by_id(db, unit_id)
        return success_response(
            UnitResponse.model_validate(unit),
            "ດຶງຂໍ້ມູນຫົວໜ່ວຍສຳເລັດ"
        )
    except Exception:
        return error_response("NOT_FOUND", "ບໍ່ພົບຂໍ້ມູນຫົວໜ່ວຍ", 404)

@router.post("")
def create_unit(unit: UnitCreate, db: Session = Depends(get_db)):
    created_unit = svc.create(db, unit)
    return success_response(
        UnitResponse.model_validate(created_unit),
        "ບັນທຶກຫົວໜ່ວຍສຳເລັດ", 201
    )

@router.put("/{unit_id}")
def update_unit(unit_id: int, unit: UnitUpdate, db: Session = Depends(get_db)):
    try:
        updated_unit = svc.update(db, unit_id, unit)
        return success_response(
            UnitResponse.model_validate(updated_unit),
            "ອັບເດດຫົວໜ່ວຍສຳເລັດ"
        )
    except Exception:
        return error_response("NOT_FOUND", "ບໍ່ພົບຂໍ້ມູນຫົວໜ່ວຍ", 404)

@router.delete("/{unit_id}")
def delete_unit(unit_id: int, db: Session = Depends(get_db)):
    try:
        svc.delete(db, unit_id)
        return success_response(None, "ລຶບຫົວໜ່ວຍສຳເລັດ")
    except Exception:
        return error_response("NOT_FOUND", "ບໍ່ພົບຂໍ້ມູນຫົວໜ່ວຍ", 404)
