from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_
from app.models.registration import Registration
from app.models.registration_detail import RegistrationDetail
from app.models.fee import Fee
from app.models.subject_detail import SubjectDetail
from app.models.tuition_payment import TuitionPayment
from app.models.student import Student
from app.models.district import District
from sqlalchemy import select
from app.schemas.registration import (
    RegistrationCreate, RegistrationUpdate,
    RegistrationBulkCreate,
    RegistrationReceiptFeeItem,
    RegistrationReceiptRequest,
)
from app.configs.exceptions import NotFoundException, ConflictException, ValidationException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check
from app.enums.scholarship import ScholarshipEnum
from app.enums.registration_status import RegistrationStatusEnum
from app.enums.discount_description import DiscountDescriptionEnum
from app.enums.academic_status import AcademicStatusEnum
from app.models.discount import Discount
from app.models.academic_years import AcademicYear
from decimal import Decimal
from datetime import date, timedelta
import time
import re


MULTI_SUBJECT_MIN_SUBJECTS = 3
LATE_REGISTRATION_THRESHOLD_DAYS = 14


def generate_registration_id(db: Session, academic_id: str) -> str:
    academic_year = db.query(AcademicYear).filter(
        AcademicYear.academic_id == academic_id
    ).first()

    if not academic_year:
        raise NotFoundException("ບໍ່ພົບສົກຮຽນ")

    year = academic_year.academic_year.split('-')[-1]
    prefix = f'R{year}-'

    latest = db.query(Registration).filter(
        Registration.registration_id.like(f'{prefix}%')
    ).order_by(
        func.length(Registration.registration_id).desc(),
        Registration.registration_id.desc()
    ).first()

    if latest and latest.registration_id:
        match = re.match(rf'{re.escape(prefix)}(\d+)', latest.registration_id)
        next_num = int(match.group(1)) + 1 if match else 1
    else:
        next_num = 1

    return f'{prefix}{next_num:04d}'


def get_all(db: Session, academic_id: str = None, all_years: bool = False):
    """
    ດຶງລາຍການລົງທະບຽນທັງໝົດ.
    - academic_id: ສະເພາະສົກຮຽນທີ່ລະບຸ.
    - all_years=True: ທຸກສົກຮຽນ (ບໍ່ filter).
    - ບໍ່ລະບຸທັງສອງ: default = ສົກທີ່ ACTIVE.
    """
    if academic_id is None and not all_years:
        active_year = db.query(AcademicYear).filter(
            AcademicYear.status == AcademicStatusEnum.ACTIVE
        ).first()
        academic_id = active_year.academic_id if active_year else None

    query = db.query(Registration).options(
        joinedload(Registration.student)
        .joinedload(Student.district)
        .joinedload(District.province),
        joinedload(Registration.discount),
        joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.academic_year),
        joinedload(Registration.tuition_payments)
    )

    if academic_id is not None:
        query = query.join(
            RegistrationDetail, Registration.registration_id == RegistrationDetail.registration_id
        ).join(
            Fee, RegistrationDetail.fee_id == Fee.fee_id
        ).filter(
            Fee.academic_id == academic_id
        ).distinct()

    return query.order_by(Registration.registration_date.desc()).all()


def get_by_id(db: Session, registration_id: str) -> Registration:
    obj = db.query(Registration).options(
        joinedload(Registration.student)
        .joinedload(Student.district)
        .joinedload(District.province),
        joinedload(Registration.discount),
        joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.academic_year),
        joinedload(Registration.tuition_payments)
    ).filter(Registration.registration_id == registration_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນການລົງທະບຽນ")
    return obj


def get_registration_by_student(db: Session, student_id: str, academic_id: str = None):
    """
    ດຶງ registration ຂອງ student ໃນສົກຮຽນ (default = ສົກທີ່ ACTIVE) ພ້ອມລາຍລະອຽດວິຊາ.
    ສົ່ງຄືນ None ຖ້າຍັງບໍ່ມີການລົງທະບຽນ.
    """
    if academic_id is None:
        active_year = db.query(AcademicYear).filter(
            AcademicYear.status == AcademicStatusEnum.ACTIVE
        ).first()
        if active_year is None:
            return None
        academic_id = active_year.academic_id

    registration = db.query(Registration).options(
        joinedload(Registration.student),
        joinedload(Registration.discount),
        joinedload(Registration.tuition_payments),
        joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.academic_year),
        joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.subject),
        joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.level),
    ).join(
        RegistrationDetail, Registration.registration_id == RegistrationDetail.registration_id
    ).join(
        Fee, RegistrationDetail.fee_id == Fee.fee_id
    ).filter(
        Registration.student_id == student_id,
        Fee.academic_id == academic_id,
    ).first()

    return registration


def build_receipt_request(db: Session, registration_id: str) -> RegistrationReceiptRequest:
    obj = db.query(Registration).options(
        joinedload(Registration.student),
        joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.subject),
        joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.level),
    ).filter(Registration.registration_id == registration_id).first()

    if not obj:
        raise NotFoundException("ຂໍ້ມູນການລົງທະບຽນ")

    selected_fees: list[RegistrationReceiptFeeItem] = []
    tuition_fee = Decimal('0')

    for detail in obj.details or []:
        fee = detail.fee_rel
        if fee is None:
            continue

        is_scholarship = detail.scholarship == ScholarshipEnum.SCHOLARSHIP
        if not is_scholarship:
            tuition_fee += fee.fee or Decimal('0')

        subject_detail = fee.subject_detail
        subject_name = '-'
        level_name = '-'

        if subject_detail is not None:
            if subject_detail.subject is not None:
                subject_name = subject_detail.subject.subject_name
            if subject_detail.level is not None:
                level_name = subject_detail.level.level_name

        selected_fees.append(
            RegistrationReceiptFeeItem(
                subject_name=subject_name,
                level_name=level_name,
                fee=fee.fee,
                is_scholarship=is_scholarship,
            )
        )

    discount_amount = obj.total_amount - obj.final_amount
    if discount_amount < 0:
        discount_amount = Decimal('0')

    student_name = (
        f"{obj.student.student_name} {obj.student.student_lastname}".strip()
        if obj.student is not None
        else obj.registration_id
    )

    return RegistrationReceiptRequest(
        registration_id=obj.registration_id,
        registration_date=obj.registration_date,
        student_name=student_name,
        selected_fees=selected_fees,
        tuition_fee=tuition_fee,
        total_fee=obj.total_amount,
        discount_amount=discount_amount,
        net_fee=obj.final_amount,
    )


def find_existing_registration_for_academic_year(db: Session, student_id: str, academic_id: str) -> Registration:
    """
    Find if student already has a registration for the given academic year.
    Returns the registration if found, None otherwise.
    """
    existing_registration = db.query(Registration).join(
        RegistrationDetail, Registration.registration_id == RegistrationDetail.registration_id
    ).join(
        Fee, RegistrationDetail.fee_id == Fee.fee_id
    ).filter(
        Registration.student_id == student_id,
        Fee.academic_id == academic_id
    ).first()
    
    return existing_registration


def _is_late_registration(
    db: Session,
    academic_id: str,
    registration_date,
) -> bool:
    academic_year = db.query(AcademicYear).filter(
        AcademicYear.academic_id == academic_id
    ).first()
    if academic_year is None or academic_year.start_date_at is None:
        return False

    reg_date = registration_date
    if hasattr(reg_date, "date"):
        reg_date = reg_date.date()
    if not isinstance(reg_date, date):
        return False

    late_threshold = academic_year.start_date_at + timedelta(
        days=LATE_REGISTRATION_THRESHOLD_DAYS
    )
    return reg_date >= late_threshold


def _select_applicable_discount(
    db: Session,
    academic_id: str,
    non_scholarship_count: int,
    has_scholarship: bool,
    registration_date,
) -> Discount | None:
    if has_scholarship:
        return None

    def _find(description: DiscountDescriptionEnum) -> Discount | None:
        return db.query(Discount).filter(
            Discount.academic_id == academic_id,
            Discount.discount_description == description.value,
        ).first()

    if non_scholarship_count >= MULTI_SUBJECT_MIN_SUBJECTS:
        discount = _find(DiscountDescriptionEnum.MULTI_SUBJECT)
        if discount is not None:
            return discount

    if _is_late_registration(db, academic_id, registration_date):
        discount = _find(DiscountDescriptionEnum.LATE_REGISTRATION)
        if discount is not None:
            return discount

    return None


def compute_registration_amounts(
    db: Session,
    items: list[tuple],
    registration_date,
) -> dict:
    """
    Core discount/amount calculation — single source of truth.

    items: list of (Fee, ScholarshipEnum) tuples (ALL subjects of the registration).
    ໃຊ້ໄດ້ທັງ preview (ບໍ່ແຕະ DB) ແລະ ຕອນ save.

    Returns dict: total_amount, discount_amount, final_amount,
                  discount_id, discount_description.
    """
    total_amount = Decimal('0')      # ສະເພາະວິຊາທີ່ບໍ່ໄດ້ທຶນ (ໃຊ້ເປັນຖານສ່ວນຫຼຸດນຳ)
    non_scholarship_count = 0
    has_scholarship = False
    academic_id = None

    for fee, scholarship in items:
        if fee is None:
            continue
        if academic_id is None:
            academic_id = fee.academic_id
        if scholarship == ScholarshipEnum.SCHOLARSHIP:
            has_scholarship = True
            continue
        total_amount += fee.fee or Decimal('0')
        non_scholarship_count += 1

    discount = None
    if academic_id is not None:
        discount = _select_applicable_discount(
            db,
            academic_id,
            non_scholarship_count,
            has_scholarship,
            registration_date,
        )

    discount_amount = Decimal('0')
    if discount is not None:
        percentage = Decimal(str(discount.discount_amount))
        discount_amount = (total_amount * percentage / Decimal('100')).quantize(
            Decimal('1')
        )

    final_amount = total_amount - discount_amount
    if final_amount < 0:
        final_amount = Decimal('0')

    return {
        "total_amount": total_amount,
        "discount_amount": discount_amount,
        "final_amount": final_amount,
        "discount_id": discount.discount_id if discount is not None else None,
        "discount_description": (
            discount.discount_description if discount is not None else None
        ),
    }


def _recalculate_registration_amounts(db: Session, registration: Registration):
    details = db.query(RegistrationDetail).options(
        joinedload(RegistrationDetail.fee_rel)
    ).filter(
        RegistrationDetail.registration_id == registration.registration_id
    ).all()

    items = [(d.fee_rel, d.scholarship) for d in details]
    result = compute_registration_amounts(
        db, items, registration.registration_date
    )

    registration.total_amount = result["total_amount"]
    registration.final_amount = result["final_amount"]
    registration.discount_id = result["discount_id"]


def preview_registration_amounts(
    db: Session,
    student_id: str,
    details: list,
    registration_date=None,
) -> dict:
    """
    Preview total / discount / final amount BEFORE saving — same logic as save.

    ລວມວິຊາທີ່ມີຢູ່ DB ແລ້ວ (ກໍລະນີ append) ກັບ ວິຊາໃໝ່ ທີ່ກຳລັງຈະເພີ່ມ
    ເພື່ອໃຫ້ frontend ສະແດງສ່ວນຫຼຸດ ກົງກັບຜົນຕອນບັນທຶກ.
    """
    from datetime import datetime

    if registration_date is None:
        registration_date = datetime.now()

    new_fee_ids = [d.fee_id for d in details]
    fees_by_id = {
        f.fee_id: f
        for f in db.query(Fee).filter(Fee.fee_id.in_(new_fee_ids)).all()
    }

    # ວິຊາໃໝ່ທີ່ກຳລັງຈະເພີ່ມ
    items: list[tuple] = []
    for d in details:
        fee = fees_by_id.get(d.fee_id)
        if fee is None:
            continue
        items.append((fee, ScholarshipEnum(d.scholarship)))

    # ຫາ academic_id ຈາກວິຊາໃໝ່ ເພື່ອດຶງວິຊາເກົ່າຂອງສົກນັ້ນ
    academic_id = None
    for fee, _ in items:
        academic_id = fee.academic_id
        break

    if academic_id is not None:
        existing = find_existing_registration_for_academic_year(
            db, student_id, academic_id
        )
        if existing is not None:
            existing_details = db.query(RegistrationDetail).options(
                joinedload(RegistrationDetail.fee_rel)
            ).filter(
                RegistrationDetail.registration_id == existing.registration_id
            ).all()
            for ed in existing_details:
                items.append((ed.fee_rel, ed.scholarship))
            # ໃຊ້ registration_date ເດີມ ເພື່ອໃຫ້ການກວດ late ສອດຄ່ອງ
            registration_date = existing.registration_date

    return compute_registration_amounts(db, items, registration_date)


def _recalculate_registration_status(db: Session, registration_id: str):

    registration = db.query(Registration).filter(
        Registration.registration_id == registration_id
    ).first()
    if not registration:
        return

    # Sum all tuition payments for this registration
    total_paid = db.query(func.sum(TuitionPayment.paid_amount)).filter(
        TuitionPayment.registration_id == registration_id
    ).scalar() or 0

    final_amount = float(registration.final_amount)
    total_paid = float(total_paid)

    # Determine status based on payment vs final amount
    if total_paid == 0:
        new_status = RegistrationStatusEnum.UNPAID
    elif total_paid >= final_amount:
        new_status = RegistrationStatusEnum.PAID
    else:
        new_status = RegistrationStatusEnum.PARTIAL

    registration.status = new_status
    db.commit()
    db.refresh(registration)


def get_total_paid(db: Session, registration_id: str) -> Decimal:
    """ລວມຍອດເງິນທີ່ຈ່າຍແລ້ວທັງໝົດຂອງການລົງທະບຽນ."""
    total = db.query(func.sum(TuitionPayment.paid_amount)).filter(
        TuitionPayment.registration_id == registration_id
    ).scalar()
    return Decimal(str(total)) if total is not None else Decimal('0')


def is_registration_locked(db: Session, registration_id: str) -> bool:
    """ຈ່າຍແລ້ວ (paid > 0) → ລັອກການແກ້ໄຂ/ລຶບວິຊາເກົ່າ."""
    return get_total_paid(db, registration_id) > 0


def recompute_registration(db: Session, registration_id: str):
    """
    ຄຳນວນ amount/discount/final + status ຄືນ ຫຼັງມີການແກ້ໄຂ/ລຶບວິຊາ.
    ຖ້າບໍ່ເຫຼືອວິຊາໃດເລີຍ → ລຶບການລົງທະບຽນ.
    """
    registration = db.query(Registration).filter(
        Registration.registration_id == registration_id
    ).first()
    if registration is None:
        return None

    remaining = db.query(RegistrationDetail).filter(
        RegistrationDetail.registration_id == registration_id
    ).count()

    if remaining == 0:
        db.delete(registration)
        db.commit()
        return None

    _recalculate_registration_amounts(db, registration)
    db.commit()
    db.refresh(registration)
    _recalculate_registration_status(db, registration_id)
    db.refresh(registration)
    return registration


def create(db: Session, data: RegistrationCreate):
    obj = Registration(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def _validate_registration_details(db: Session, student_id: str, details: list, academic_id: str = None):
    """Validate registration details before creating or appending"""
    if not details:
        raise ValidationException("ລາຍລະອຽດການລົງທະບຽນບໍ່ໄດ້ຖືກສະຫນອງ")
    
    # Maximum 3 subjects per request
    if len(details) > 3:
        raise ValidationException("ນັກຮຽນສາມາດລົງທະບຽນໄດ້ສູງສຸດ 3 ວິຊາຕໍ່ຄັ້ງ")
    
    fee_ids = [d.fee_id for d in details]
    if len(fee_ids) != len(set(fee_ids)):
        raise ValidationException("ບໍ່ສາມາດລົງທະບຽນວິຊາດຽວກັນຫຼາຍຄັ້ງໄດ້")
    
    # Verify all fees exist
    fees = db.query(Fee).filter(Fee.fee_id.in_(fee_ids)).all()
    if not fees or len(fees) != len(fee_ids):
        raise ValidationException("ບາງວິຊາບໍ່ມີຂໍ້ມູນ")
    
    # All fees must be from same academic year
    academic_ids_in_request = set(f.academic_id for f in fees)
    if len(academic_ids_in_request) > 1:
        raise ValidationException("ບໍ່ສາມາດລົງທະບຽນວິຊາຈາກບົດຮຽນທີ່ແຕກຕ່າງກັນໄດ້")
    
    request_academic_id = list(academic_ids_in_request)[0]
    
    # Check if student already registered for any of these fees
    existing_details = db.query(RegistrationDetail).join(
        Registration, RegistrationDetail.registration_id == Registration.registration_id
    ).filter(
        Registration.student_id == student_id,
        RegistrationDetail.fee_id.in_(fee_ids)
    ).first()
    
    if existing_details:
        raise ConflictException("ນັກຮຽນໄດ້ລົງທະບຽນວິຊານີ້ແລ້ວ")
    
    # Check total registration count for this academic year (including existing)
    current_count = db.query(RegistrationDetail).join(
        Registration, RegistrationDetail.registration_id == Registration.registration_id
    ).join(
        Fee, RegistrationDetail.fee_id == Fee.fee_id
    ).filter(
        Registration.student_id == student_id,
        Fee.academic_id == request_academic_id
    ).count()
    
    # Maximum 3 subjects total per academic year
    if current_count + len(fee_ids) > 3:
        raise ValidationException(f"ນັກຮຽນສາມາດລົງທະບຽນໄດ້ສູງສຸດ 3 ວິຊາຕໍ່ສົກຮຽນ")
    
    return request_academic_id


def create_bulk(db: Session, data: RegistrationBulkCreate, max_retries: int = 3):
    """
    Create or append registration for student.
    
    Logic:
    - If student already has registration for this academic year: APPEND fees and update amounts
    - If student is new to this academic year: CREATE new registration
    
    This ensures one registration per academic year per student.
    """
    
    # Validate and get academic_id
    academic_id = _validate_registration_details(db, data.student_id, data.details)

    for attempt in range(max_retries):
        try:
            db.execute(
                select(Registration).filter(
                    Registration.student_id == data.student_id
                ).with_for_update(skip_locked=False)
            ).scalars().all()

            # Check if student already has registration for this academic year
            existing_registration = find_existing_registration_for_academic_year(
                db, data.student_id, academic_id
            )

            if existing_registration:
                # APPEND: Add new fees to existing registration
                for detail in data.details:
                    reg_detail = RegistrationDetail(
                        registration_id=existing_registration.registration_id,
                        fee_id=detail.fee_id,
                        scholarship=ScholarshipEnum(detail.scholarship)
                    )
                    db.add(reg_detail)
                db.flush()

                # Recompute amounts + discount from ALL details (old + new)
                _recalculate_registration_amounts(db, existing_registration)

                db.commit()
                db.refresh(existing_registration)

                # Recalculate status based on payments vs updated final_amount
                _recalculate_registration_status(db, existing_registration.registration_id)
                db.refresh(existing_registration)

                return existing_registration

            else:
                # CREATE: New registration for this student + academic year
                registration_id = data.registration_id or generate_registration_id(db, academic_id)

                # Verify ID is unique
                existing = db.query(Registration).filter(
                    Registration.registration_id == registration_id
                ).first()

                if existing:
                    registration_id = generate_registration_id(db, academic_id)
                    if attempt < max_retries - 1:
                        time.sleep(0.1)
                        continue

                registration = Registration(
                    registration_id=registration_id,
                    student_id=data.student_id,
                    discount_id=None,
                    total_amount=Decimal('0'),
                    final_amount=Decimal('0'),
                    status=data.status,
                    registration_date=data.registration_date
                )
                db.add(registration)
                db.flush()

                # Add all details
                for detail in data.details:
                    reg_detail = RegistrationDetail(
                        registration_id=registration_id,
                        fee_id=detail.fee_id,
                        scholarship=ScholarshipEnum(detail.scholarship)
                    )
                    db.add(reg_detail)
                db.flush()

                # Compute amounts + discount on the backend (source of truth)
                _recalculate_registration_amounts(db, registration)

                db.commit()
                db.refresh(registration)
                return registration
        
        except IntegrityError as e:
            db.rollback()
            if attempt == max_retries - 1:
                error_msg = str(e)
                if "Duplicate entry" in error_msg and "registration_id" in error_msg:
                    raise ConflictException(f"ບໍ່ສາມາດລົງທະບຽນໄດ້: ID ຊໍ້າກັນ ({max_retries} ຄັ້ງ)")
                elif "Duplicate entry" in error_msg:
                    raise ConflictException("ລົງທະບຽນຊໍ້າກັນ ກະລຸນາລອງໃໝ່")
                else:
                    raise ConflictException(f"ຜິດພາດ database: {str(e)}")
            
            time.sleep(0.1)
            continue
        
        except Exception as e:
            db.rollback()
            raise
    
    raise ConflictException(f"ບໍ່ສາມາດລົງທະບຽນໄດ້ຫຼັງຈາກລອງ {max_retries} ຄັ້ງ")


def update(db: Session, registration_id: str, data: RegistrationUpdate):
    obj = get_by_id(db, registration_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, registration_id: str):
    obj = get_by_id(db, registration_id)

    db.expire(obj)

    from app.models.tuition_payment import TuitionPayment
    db.query(TuitionPayment).filter(
        TuitionPayment.registration_id == registration_id
    ).delete(synchronize_session='fetch')

    db.query(RegistrationDetail).filter(
        RegistrationDetail.registration_id == registration_id
    ).delete(synchronize_session='fetch')

    safe_delete_with_constraint_check(db, obj, "registration")
