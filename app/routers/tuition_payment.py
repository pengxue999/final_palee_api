from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.configs.database import get_db
from app.schemas.tuition_payment import TuitionPaymentCreate, TuitionPaymentUpdate, TuitionPaymentResponse
from app.configs.response import success_response
from app.services import tuition_payment as svc
from app.services import receipt_pdf as receipt_pdf_svc

router = APIRouter(prefix="/tuition-payments", tags=["ການຈ່າຍຄ່າຮຽນ"])


@router.get("")
def get_all(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [TuitionPaymentResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນການຈ່າຍຄ່າຮຽນທັງໝົດສຳເລັດ"
    )


@router.get("/by-registration/{registration_id}")
def get_by_registration(registration_id: str, db: Session = Depends(get_db)):
    data = svc.get_by_registration(db, registration_id)
    return success_response(
        [TuitionPaymentResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນການຈ່າຍຄ່າຮຽນຕາມລົງທະບຽນສຳເລັດ"
    )


@router.get("/by-registration/{registration_id}/history-pdf")
def get_payment_history_pdf(registration_id: str, db: Session = Depends(get_db)):
    report_data = svc.build_payment_history_report_request(db, registration_id)
    pdf_bytes = receipt_pdf_svc.build_tuition_payment_history_report_pdf(report_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
    )


@router.get("/{payment_id}")
def get_one(payment_id: str, db: Session = Depends(get_db)):
    return success_response(
        TuitionPaymentResponse.model_validate(svc.get_by_id(db, payment_id)),
        "ດຶງຂໍ້ມູນການຈ່າຍຄ່າຮຽນສຳເລັດ"
    )


@router.get("/{payment_id}/receipt-pdf")
def get_receipt_pdf(payment_id: str, db: Session = Depends(get_db)):
    receipt_data = svc.build_receipt_request(db, payment_id)
    pdf_bytes = receipt_pdf_svc.build_tuition_payment_receipt_pdf(receipt_data)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
    )


@router.post("")
def create(data: TuitionPaymentCreate, db: Session = Depends(get_db)):
    return success_response(
        TuitionPaymentResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກການຈ່າຍຄ່າຮຽນສຳເລັດ", 201
    )


@router.put("/{payment_id}")
def update(payment_id: str, data: TuitionPaymentUpdate, db: Session = Depends(get_db)):
    return success_response(
        TuitionPaymentResponse.model_validate(svc.update(db, payment_id, data)),
        "ອັບເດດການຈ່າຍຄ່າຮຽນສຳເລັດ"
    )


@router.delete("/{payment_id}")
def delete(payment_id: str, db: Session = Depends(get_db)):
    svc.delete(db, payment_id)
    return success_response(None, "ລຶບການຈ່າຍຄ່າຮຽນສຳເລັດ")
