from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func, and_
from app.models.registration import Registration
from app.models.registration_detail import RegistrationDetail
from app.models.fee import Fee
from app.models.subject_detail import SubjectDetail
from app.models.tuition_payment import TuitionPayment
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
from decimal import Decimal
import time
import re


def generate_registration_id(db: Session) -> str:
    latest = db.query(Registration).order_by(
        func.length(Registration.registration_id).desc(),
        Registration.registration_id.desc()
    ).first()

    if latest and latest.registration_id:
        match = re.match(r'R(\d+)', latest.registration_id)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f'R{next_num:04d}'


def get_all(db: Session):
    return db.query(Registration).options(
        joinedload(Registration.student),
        joinedload(Registration.discount),
        joinedload(Registration.tuition_payments)
    ).order_by(Registration.registration_date.desc()).all()


def get_by_id(db: Session, registration_id: str) -> Registration:
    obj = db.query(Registration).options(
        joinedload(Registration.student),
        joinedload(Registration.discount),
        joinedload(Registration.tuition_payments)
    ).filter(Registration.registration_id == registration_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນການລົງທະບຽນ")
    return obj


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


def _recalculate_registration_status(db: Session, registration_id: str):
    """
    Recalculate and update registration status based on total paid amount vs final_amount.
    
    This is called after updating registration amounts (when appending fees).
    """
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
    
    # Calculate total fee amount
    fee_ids = [d.fee_id for d in data.details]
    fees = db.query(Fee).filter(Fee.fee_id.in_(fee_ids)).all()
    new_fee_total = sum(Decimal(str(f.fee)) for f in fees)
    
    for attempt in range(max_retries):
        try:
            # Lock the student's registrations to prevent race conditions
            db.execute(
                select(Registration).filter(
                    Registration.student_id == data.student_id
                ).with_for_update(skip_locked=False)
            )
            
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
                
                # Update total and final amounts
                existing_registration.total_amount = Decimal(str(existing_registration.total_amount)) + new_fee_total
                existing_registration.final_amount = existing_registration.total_amount
                
                # If new discount provided, update it
                if data.discount_id:
                    existing_registration.discount_id = data.discount_id
                
                db.commit()
                db.refresh(existing_registration)
                
                # Recalculate status based on payments vs updated final_amount
                _recalculate_registration_status(db, existing_registration.registration_id)
                db.refresh(existing_registration)
                
                return existing_registration
            
            else:
                # CREATE: New registration for this student + academic year
                registration_id = data.registration_id or generate_registration_id(db)
                
                # Verify ID is unique
                existing = db.query(Registration).filter(
                    Registration.registration_id == registration_id
                ).first()
                
                if existing:
                    registration_id = generate_registration_id(db)
                    if attempt < max_retries - 1:
                        time.sleep(0.1)
                        continue
                
                registration = Registration(
                    registration_id=registration_id,
                    student_id=data.student_id,
                    discount_id=data.discount_id,
                    total_amount=data.total_amount,
                    final_amount=data.final_amount,
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
