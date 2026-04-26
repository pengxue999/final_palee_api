from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from decimal import Decimal
from app.configs.database import get_db
from app.schemas.registration import (
    RegistrationCreate,
    RegistrationUpdate,
    RegistrationResponse,
    RegistrationBulkCreate,
    RegistrationReceiptRequest,
)
from app.configs.response import success_response
from app.services import registration as svc
from app.services import receipt_pdf as receipt_pdf_svc

router = APIRouter(prefix="/registrations", tags=["ການລົງທະບຽນ"])


def _calc_paid(obj) -> Decimal:
    return sum((tp.paid_amount for tp in (obj.tuition_payments or [])), Decimal('0'))


@router.get("")
def get_registrations(db: Session = Depends(get_db)):
    data = svc.get_all(db)
    return success_response(
        [RegistrationResponse.model_validate(item, paid_amount=_calc_paid(item)) for item in data],
        "ດຶງຂໍ້ມູນການລົງທະບຽນທັງໝົດສຳເລັດ"
    )


@router.get("/{registration_id}")
def get_registration(registration_id: str, db: Session = Depends(get_db)):
    item = svc.get_by_id(db, registration_id)
    return success_response(
        RegistrationResponse.model_validate(item, paid_amount=_calc_paid(item)),
        "ດຶງຂໍ້ມູນການລົງທະບຽນສຳເລັດ"
    )


@router.get("/{registration_id}/receipt-pdf")
def get_registration_receipt_pdf(
    registration_id: str,
    db: Session = Depends(get_db),
):
    receipt_data = svc.build_receipt_request(db, registration_id)
    pdf_bytes = receipt_pdf_svc.build_registration_receipt_pdf(receipt_data)
    filename = f'registration_{registration_id}.pdf'
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post("")
def create_registration(data: RegistrationCreate, db: Session = Depends(get_db)):
    item = svc.create(db, data)
    return success_response(
        RegistrationResponse.model_validate(item, paid_amount=_calc_paid(item)),
        "ບັນທຶກການລົງທະບຽນສຳເລັດ", 201
    )


@router.post("/bulk")
def create_bulk_registration(data: RegistrationBulkCreate, db: Session = Depends(get_db)):
    """Create registration with details in one request"""
    item = svc.create_bulk(db, data)
    return success_response(
        RegistrationResponse.model_validate(item, paid_amount=_calc_paid(item)),
        "ບັນທຶກການລົງທະບຽນ ແລະ ລາຍລະອຽດສຳເລັດ", 201
    )


@router.post("/receipt-pdf")
def create_registration_receipt_pdf(data: RegistrationReceiptRequest):
    pdf_bytes = receipt_pdf_svc.build_registration_receipt_pdf(data)
    filename = f'registration_{data.registration_id}.pdf'
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.put("/{registration_id}")
def update_registration(registration_id: str, data: RegistrationUpdate, db: Session = Depends(get_db)):
    item = svc.update(db, registration_id, data)
    return success_response(
        RegistrationResponse.model_validate(item, paid_amount=_calc_paid(item)),
        "ອັບເດດການລົງທະບຽນສຳເລັດ"
    )


@router.delete("/{registration_id}")
def delete_registration(registration_id: str, db: Session = Depends(get_db)):
    svc.delete(db, registration_id)
    return success_response(None, "ລຶບການລົງທະບຽນສຳເລັດ")
