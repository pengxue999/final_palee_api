from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.configs.database import get_db
from app.schemas.salary_payment import SalaryPaymentCreate, SalaryPaymentUpdate, SalaryPaymentResponse
from app.configs.response import success_response
from app.services import salary_payment as svc
from app.services import receipt_pdf as receipt_pdf_svc

router = APIRouter(prefix="/salary-payments", tags=["ການຈ່າຍເງິນເດືອນ"])


@router.get("")
def get_all(
    teacher_id: Optional[str] = None,
    year: Optional[int] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    data = svc.get_all(db, teacher_id=teacher_id, year=year, month=month)
    return success_response(
        [SalaryPaymentResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນການຈ່າຍເງິນເດືອນທັງໝົດສຳເລັດ"
    )


@router.get("/options/teaching-months")
def get_teaching_months(
    teacher_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get available months from teaching logs for period selection."""
    data = svc.get_teaching_months(db, teacher_id=teacher_id)
    return success_response(data, "ດຶງຂໍ້ມູນເດືອນທີ່ມີການສອນສຳເລັດ")


@router.get("/teachers/monthly")
def get_monthly_teachers_summary(
    month: int = Query(..., description="Month 1-12"),
    year: Optional[int] = Query(None, description="Year (e.g. 2026), defaults to current year"),
    db: Session = Depends(get_db)
):
    """Get all teachers with their salary summary for a specific month."""
    year = year or datetime.now().year
    data = svc.get_monthly_teachers_summary(db, year, month)
    return success_response(data, "ດຶງຂໍ້ມູນສະຫຼຸບອາຈານປະຈຳເດືອນສຳເລັດ")


@router.get("/teacher/{teacher_id}/payments")
def get_by_teacher(teacher_id: str, db: Session = Depends(get_db)):
    """Get all payments for a specific teacher."""
    data = svc.get_by_teacher(db, teacher_id)
    return success_response(
        [SalaryPaymentResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນການຈ່າຍເງິນຂອງອາຈານສຳເລັດ"
    )


@router.get("/calculate/{teacher_id}")
def calculate_salary(
    teacher_id: str,
    month: int = Query(..., description="Month 1-12"),
    year: Optional[int] = Query(None, description="Year (e.g. 2026), defaults to current year"),
    db: Session = Depends(get_db)
):
    """Calculate teacher salary for a specific month.

    Returns actual (based on attended sessions), planned (full month),
    total paid, and remaining balance including prior-month advance deductions.
    """
    year = year or datetime.now().year
    data = svc.calculate_teacher_salary(db, teacher_id, year, month)
    return success_response(data, "ຄິດໄລ່ເງິນສອນສຳເລັດ")


@router.get("/teacher/{teacher_id}/summary")
def get_teacher_summary(
    teacher_id: str,
    month: int = Query(..., description="Month 1-12"),
    year: Optional[int] = Query(None, description="Year (e.g. 2026), defaults to current year"),
    db: Session = Depends(get_db)
):
    """Get payment summary for a teacher in a specific month."""
    year = year or datetime.now().year
    data = svc.get_payment_summary_by_teacher(db, teacher_id, year, month)
    return success_response(data, "ດຶງຂໍ້ມູນສະຫຼຸບການຈ່າຍເງິນສຳເລັດ")


@router.get("/{payment_id}")
def get_one(payment_id: str, db: Session = Depends(get_db)):
    return success_response(
        SalaryPaymentResponse.model_validate(svc.get_by_id(db, payment_id)),
        "ດຶງຂໍ້ມູນການຈ່າຍເງິນເດືອນສຳເລັດ"
    )


@router.get("/{payment_id}/receipt-pdf")
def get_receipt_pdf(payment_id: str, db: Session = Depends(get_db)):
    receipt_data = svc.build_receipt_request(db, payment_id)
    pdf_bytes = receipt_pdf_svc.build_salary_payment_receipt_pdf(receipt_data)
    filename = f'salary_payment_{payment_id}.pdf'
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )


@router.post("")
def create(data: SalaryPaymentCreate, db: Session = Depends(get_db)):
    return success_response(
        SalaryPaymentResponse.model_validate(svc.create(db, data)),
        "ບັນທຶກການຈ່າຍເງິນເດືອນສຳເລັດ", 201
    )


@router.put("/{payment_id}")
def update(payment_id: str, data: SalaryPaymentUpdate, db: Session = Depends(get_db)):
    return success_response(
        SalaryPaymentResponse.model_validate(svc.update(db, payment_id, data)),
        "ອັບເດດການຈ່າຍເງິນເດືອນສຳເລັດ"
    )


@router.delete("/{payment_id}")
def delete(payment_id: str, db: Session = Depends(get_db)):
    svc.delete(db, payment_id)
    return success_response(None, "ລຶບການຈ່າຍເງິນເດືອນສຳເລັດ")
