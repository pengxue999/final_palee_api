from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.evaluation import (
    EvaluationCreate,
    EvaluationUpdate,
    EvaluationResponse,
    ScoreEntrySaveRequest,
)
from app.configs.response import success_response, error_response
from app.services import evaluation as svc

router = APIRouter(prefix="/evaluations", tags=["ການປະເມີນຜົນ"])


@router.get("/score-entry/sheet")
def get_score_entry_sheet(
    semester: str = Query(...),
    level_id: str = Query(...),
    subject_detail_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return success_response(
        svc.get_score_entry_sheet(db, semester, level_id, subject_detail_id),
        "ດຶງຂໍ້ມູນຟອມປ້ອນຄະແນນສຳເລັດ",
    )


@router.get("/score-entry/subjects")
def get_score_entry_subjects(
    db: Session = Depends(get_db),
):
    return success_response(
        svc.get_score_entry_subjects(db),
        "ດຶງລາຍການວິຊາສຳລັບປ້ອນຄະແນນສຳເລັດ",
    )


@router.get("/score-entry/levels")
def get_score_entry_levels(
    subject_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return success_response(
        svc.get_score_entry_levels(db, subject_id),
        "ດຶງລາຍການລະດັບສຳລັບປ້ອນຄະແນນສຳເລັດ",
    )


@router.post("/score-entry/preview")
def preview_score_entry_sheet(data: ScoreEntrySaveRequest, db: Session = Depends(get_db)):
    return success_response(
        svc.preview_score_entry_sheet(db, data),
        "ຄຳນວນການຈັດອັນດັບ ແລະ ລາງວັນສຳເລັດ",
    )


@router.put("/score-entry/sheet")
def save_score_entry_sheet(data: ScoreEntrySaveRequest, db: Session = Depends(get_db)):
    return success_response(
        svc.save_score_entry_sheet(db, data),
        "ບັນທຶກຄະແນນສຳເລັດ",
    )


@router.get("")
def get_evaluations(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [EvaluationResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນການປະເມີນຜົນທັງໝົດສຳເລັດ"
    )


@router.get("/{evaluation_id}")
def get_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    obj = svc.get_by_id(db, evaluation_id)
    if not obj:
        return error_response("NOT_FOUND", "ບໍ່ພົບການປະເມີນຜົນ", 404)
    return success_response(
        EvaluationResponse.model_validate(obj),
        "ດຶງຂໍ້ມູນການປະເມີນຜົນສຳເລັດ"
    )


@router.post("")
def create_evaluation(data: EvaluationCreate, db: Session = Depends(get_db)):
    return success_response(
        EvaluationResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກການປະເມີນຜົນສຳເລັດ", 201
    )


@router.put("/{evaluation_id}")
def update_evaluation(evaluation_id: str, data: EvaluationUpdate, db: Session = Depends(get_db)):
    obj = svc.update(db, evaluation_id, data)
    if not obj:
        return error_response("NOT_FOUND", "ບໍ່ພົບການປະເມີນຜົນ", 404)
    return success_response(
        EvaluationResponse.model_validate(obj),
        "ອັບເດດການປະເມີນຜົນສຳເລັດ"
    )


@router.delete("/{evaluation_id}")
def delete_evaluation(evaluation_id: str, db: Session = Depends(get_db)):
    if not svc.delete(db, evaluation_id):
        return error_response("NOT_FOUND", "ບໍ່ພົບການປະເມີນຜົນ", 404)
    return success_response(None, "ລຶບການປະເມີນຜົນສຳເລັດ")
