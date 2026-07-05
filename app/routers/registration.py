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
    RegistrationPreviewRequest,
    RegistrationPreviewResponse,
    StudentRegistrationResponse,
    StudentRegistrationDetailItem,
)
from app.enums.scholarship import ScholarshipEnum
from app.configs.response import success_response
from app.services import registration as svc
from app.services import receipt_pdf as receipt_pdf_svc

router = APIRouter(prefix="/registrations", tags=["ການລົງທະບຽນ"])


def _calc_paid(obj) -> Decimal:
    return sum((tp.paid_amount for tp in (obj.tuition_payments or [])), Decimal('0'))


@router.get("")
def get_registrations(
    academic_id: str | None = None,
    all_years: bool = False,
    db: Session = Depends(get_db),
):
    data = svc.get_all(db, academic_id=academic_id, all_years=all_years)
    return success_response(
        [RegistrationResponse.model_validate(item, paid_amount=_calc_paid(item)) for item in data],
        "ດຶງຂໍ້ມູນການລົງທະບຽນທັງໝົດສຳເລັດ"
    )


def _scholarship_value(scholarship) -> str:
    return scholarship.value if hasattr(scholarship, "value") else str(scholarship)


@router.get("/by-student/{student_id}")
def get_registration_by_student(student_id: str, db: Session = Depends(get_db)):
    """
    Get a student's existing registration (active academic year) with its subjects.
    Returns null data if the student has no registration yet.
    """
    reg = svc.get_registration_by_student(db, student_id)
    if reg is None:
        return success_response(None, "ນັກຮຽນຍັງບໍ່ມີການລົງທະບຽນໃນສົກນີ້")

    paid = _calc_paid(reg)

    academic_id = None
    academic_year = None
    details: list[StudentRegistrationDetailItem] = []

    for d in reg.details or []:
        fee = getattr(d, "fee_rel", None)
        if fee is None:
            continue
        if academic_id is None:
            year = getattr(fee, "academic_year", None)
            if year is not None:
                academic_id = year.academic_id
                academic_year = year.academic_year

        subject_detail = getattr(fee, "subject_detail", None)
        subject_name = "-"
        level_name = "-"
        if subject_detail is not None:
            if subject_detail.subject is not None:
                subject_name = subject_detail.subject.subject_name
            if subject_detail.level is not None:
                level_name = subject_detail.level.level_name

        details.append(
            StudentRegistrationDetailItem(
                regis_detail_id=d.regis_detail_id,
                fee_id=d.fee_id,
                subject_name=subject_name,
                level_name=level_name,
                scholarship=_scholarship_value(d.scholarship),
                fee=fee.fee,
            )
        )

    status_value = reg.status.value if hasattr(reg.status, "value") else reg.status

    response = StudentRegistrationResponse(
        registration_id=reg.registration_id,
        student_id=reg.student_id,
        academic_id=academic_id,
        academic_year=academic_year,
        discount_id=reg.discount_id,
        discount_description=(
            reg.discount.discount_description if reg.discount else None
        ),
        total_amount=reg.total_amount,
        final_amount=reg.final_amount,
        paid_amount=paid,
        status=status_value,
        registration_date=reg.registration_date,
        is_locked=paid > 0,
        details=details,
    )
    return success_response(response, "ດຶງຂໍ້ມູນການລົງທະບຽນຂອງນັກຮຽນສຳເລັດ")


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
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
    )


@router.post("")
def create_registration(data: RegistrationCreate, db: Session = Depends(get_db)):
    item = svc.create(db, data)
    return success_response(
        RegistrationResponse.model_validate(item, paid_amount=_calc_paid(item)),
        "ບັນທຶກການລົງທະບຽນສຳເລັດ", 201
    )


@router.post("/preview")
def preview_registration(data: RegistrationPreviewRequest, db: Session = Depends(get_db)):
    """Preview total/discount/final amounts before saving (backend is source of truth)."""
    result = svc.preview_registration_amounts(
        db,
        student_id=data.student_id,
        details=data.details,
        registration_date=data.registration_date,
    )
    return success_response(
        RegistrationPreviewResponse(**result),
        "ຄຳນວນສ່ວນຫຼຸດສຳເລັດ",
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
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
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
