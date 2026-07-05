"""
Public router — endpoints ສາທາລະນະ ສຳລັບ web portfolio (ບໍ່ຕ້ອງ login).

ສ່ວນນີ້ເປີດໃຫ້ນັກຮຽນ:
  - ເບິ່ງຂໍ້ມູນສູນ (ແຂວງ, ເມືອງ, ວິຊາ, ຄ່າຮຽນ, ສ່ວນຫຼຸດ)
  - ລົງທະບຽນອອນລາຍ (ສ້າງ student + registration)

⚠️ ເປີດສະເພາະ endpoint ທີ່ portfolio ໃຊ້ ແລະ ປອດໄພ ເທົ່ານັ້ນ.
   ບໍ່ເປີດ list/get/delete ຂອງ students ຫຼື registrations (ກັນຂໍ້ມູນສ່ວນຕົວຮົ່ວ).
   router admin ທັງໝົດຍັງ protected ດ້ວຍ login ຄືເກົ່າ.
"""

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from decimal import Decimal

from app.configs.database import get_db
from app.configs.response import success_response

from app.schemas.province import ProvinceResponse
from app.schemas.district import DistrictResponse
from app.schemas.subject_detail import SubjectDetailResponse
from app.schemas.fee import FeeResponse
from app.schemas.discount import DiscountResponse
from app.schemas.academic_years import AcademicYearResponse
from app.schemas.student import StudentCreate, StudentResponse
from app.schemas.registration import (
    RegistrationBulkCreate,
    RegistrationResponse,
    RegistrationReceiptRequest,
)
from app.schemas.user import UserCreate, UserResponse

from app.configs.exceptions import BaseAPIException
from app.models.user import User

from app.services import province as province_svc
from app.services import district as district_svc
from app.services import subject_detail as subject_detail_svc
from app.services import fee as fee_svc
from app.services import discount as discount_svc
from app.services import academic_years as academic_year_svc
from app.services import student as student_svc
from app.services import registration as registration_svc
from app.services import receipt_pdf as receipt_pdf_svc
from app.services import user as user_svc

router = APIRouter(prefix="/public", tags=["public"])


def _calc_paid(obj) -> Decimal:
    return sum((tp.paid_amount for tp in (obj.tuition_payments or [])), Decimal("0"))


# ── ຂໍ້ມູນ reference (read-only) ─────────────────────────────────────────────
@router.get("/provinces")
def get_provinces(db: Session = Depends(get_db)):
    data = province_svc.get_all(db)
    return success_response(
        [ProvinceResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນແຂວງທັງໝົດສຳເລັດ",
    )


@router.get("/districts/province/{province_id}")
def get_districts_by_province(province_id: int, db: Session = Depends(get_db)):
    data = district_svc.get_by_province_id(db, province_id)
    return success_response(
        [DistrictResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນເມືອງຕາມແຂວງສຳເລັດ",
    )


@router.get("/subject-details")
def get_subject_details(db: Session = Depends(get_db)):
    data = subject_detail_svc.get_all(db)
    return success_response(
        [SubjectDetailResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນລາຍລະອຽດວິຊາທັງໝົດສຳເລັດ",
    )


@router.get("/fees")
def get_fees(db: Session = Depends(get_db)):
    data = fee_svc.get_all(db, active_only=True)
    return success_response(
        [FeeResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນຄ່າຮຽນທັງໝົດສຳເລັດ",
    )


@router.get("/discounts")
def get_discounts(db: Session = Depends(get_db)):
    data = discount_svc.get_all(db)
    return success_response(
        [DiscountResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນສ່ວນຫຼຸດທັງໝົດສຳເລັດ",
    )


@router.get("/academic-years")
def get_academic_years(db: Session = Depends(get_db)):
    data = academic_year_svc.get_all(db)
    return success_response(
        [AcademicYearResponse.model_validate(item) for item in data],
        "ດຶງຂໍ້ມູນສົກຮຽນທັງໝົດສຳເລັດ",
    )


# ── ລົງທະບຽນອອນລາຍ (create only) ──────────────────────────────────────────
@router.post("/students")
def create_student(data: StudentCreate, db: Session = Depends(get_db)):
    student = student_svc.create(db, data)
    return success_response(
        StudentResponse.model_validate(student),
        "ບັນທຶກນັກຮຽນສຳເລັດ",
        201,
    )


@router.post("/registrations/bulk")
def create_registration_bulk(data: RegistrationBulkCreate, db: Session = Depends(get_db)):
    item = registration_svc.create_bulk(db, data)
    return success_response(
        RegistrationResponse.model_validate(item, paid_amount=_calc_paid(item)),
        "ບັນທຶກການລົງທະບຽນ ແລະ ລາຍລະອຽດສຳເລັດ",
        201,
    )


@router.post("/registrations/receipt-pdf")
def create_registration_receipt_pdf(data: RegistrationReceiptRequest):
    pdf_bytes = receipt_pdf_svc.build_registration_receipt_pdf(data)
    return Response(content=pdf_bytes, media_type="application/pdf")


@router.post("/setup-admin")
def setup_admin(data: UserCreate, db: Session = Depends(get_db)):
    if db.query(User).first() is not None:
        raise BaseAPIException(
            code="FORBIDDEN",
            message="ລະບົບມີຜູ້ໃຊ້ແລ້ວ ບໍ່ສາມາດໃຊ້ endpoint ນີ້ໄດ້ອີກ",
            status_code=403,
        )
    user = user_svc.create(db, data)
    return success_response(
        UserResponse.model_validate(user),
        "ສ້າງຜູ້ໃຊ້ຄົນທຳອິດສຳເລັດ",
        201,
    )
