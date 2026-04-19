from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.evaluation_detail import EvaluationDetailCreate, EvaluationDetailUpdate, EvaluationDetailResponse
from app.configs.response import success_response
from app.services import evaluation_detail as svc

router = APIRouter(prefix="/evaluation-details", tags=["ລາຍລະອຽດການປະເມີນຜົນ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [EvaluationDetailResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນລາຍລະອຽດການປະເມີນຜົນທັງໝົດສຳເລັດ"
    )


@router.get("/{eval_detail_id}")
def get_one(eval_detail_id: int, db: Session = Depends(get_db)):
    return success_response(
        EvaluationDetailResponse.model_validate(svc.get_by_id(db, eval_detail_id)),
        "ດຶງຂໍ້ມູນລາຍລະອຽດການປະເມີນຜົນສຳເລັດ"
    )


@router.post("")
def create(data: EvaluationDetailCreate, db: Session = Depends(get_db)):
    return success_response(
        EvaluationDetailResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກລາຍລະອຽດການປະເມີນຜົນສຳເລັດ", 201
    )


@router.put("/{eval_detail_id}")
def update(eval_detail_id: int, data: EvaluationDetailUpdate, db: Session = Depends(get_db)):
    return success_response(
        EvaluationDetailResponse.model_validate(svc.update(db, eval_detail_id, data)),
        "ອັບເດດລາຍລະອຽດການປະເມີນຜົນສຳເລັດ"
    )


@router.delete("/{eval_detail_id}")
def delete(eval_detail_id: int, db: Session = Depends(get_db)):
    svc.delete(db, eval_detail_id)
    return success_response(None, "ລຶບລາຍລະອຽດການປະເມີນຜົນສຳເລັດ")
