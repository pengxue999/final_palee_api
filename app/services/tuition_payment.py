from decimal import Decimal

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.tuition_payment import TuitionPayment
from app.models.registration import Registration
from app.models.registration_detail import RegistrationDetail
from app.models.fee import Fee
from app.models.subject_detail import SubjectDetail
from app.models.income import Income
from app.models.student import Student
from app.schemas.tuition_payment import (
    TuitionPaymentCreate,
    TuitionPaymentHistoryItem,
    TuitionPaymentHistoryReportRequest,
    TuitionPaymentUpdate,
    TuitionPaymentReceiptRequest,
)
from app.configs.exceptions import NotFoundException
from app.enums.registration_status import RegistrationStatusEnum
import re


def generate_payment_id(db: Session) -> str:
    """Generate sequential payment ID in format TP0001, TP0002, etc."""
    latest = db.query(TuitionPayment).order_by(
        func.length(TuitionPayment.tuition_payment_id).desc(),
        TuitionPayment.tuition_payment_id.desc()
    ).first()

    if latest and latest.tuition_payment_id:
        match = re.match(r'TP(\d+)', latest.tuition_payment_id)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f'TP{next_num:04d}'


def _update_registration_status(db: Session, registration_id: str):
    """Recalculate and update registration status based on total paid amount."""
    registration = db.query(Registration).filter(
        Registration.registration_id == registration_id
    ).first()
    if not registration:
        return

    total_paid = db.query(func.sum(TuitionPayment.paid_amount)).filter(
        TuitionPayment.registration_id == registration_id
    ).scalar() or 0

    final_amount = float(registration.final_amount)
    total_paid = float(total_paid)

    if total_paid == 0:
        new_status = RegistrationStatusEnum.UNPAID
    elif total_paid >= final_amount:
        new_status = RegistrationStatusEnum.PAID
    else:
        new_status = RegistrationStatusEnum.PARTIAL

    registration.status = new_status
    db.commit()
    db.refresh(registration)  # Refresh to ensure in-memory object is up-to-date


def get_all(db: Session):
    return db.query(TuitionPayment).options(
        joinedload(TuitionPayment.registration).joinedload(Registration.student)
    ).order_by(TuitionPayment.pay_date.desc()).all()


def get_by_registration(db: Session, registration_id: str):
    return db.query(TuitionPayment).options(
        joinedload(TuitionPayment.registration).joinedload(Registration.student)
    ).filter(TuitionPayment.registration_id == registration_id).order_by(TuitionPayment.pay_date.desc()).all()


def get_by_id(db: Session, tuition_payment_id: str) -> TuitionPayment:
    obj = db.query(TuitionPayment).options(
        joinedload(TuitionPayment.registration).joinedload(Registration.student),
        joinedload(TuitionPayment.registration).joinedload(Registration.discount),
        joinedload(TuitionPayment.registration)
        .joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.subject),
        joinedload(TuitionPayment.registration)
        .joinedload(Registration.details)
        .joinedload(RegistrationDetail.fee_rel)
        .joinedload(Fee.subject_detail)
        .joinedload(SubjectDetail.level),
    ).filter(TuitionPayment.tuition_payment_id == tuition_payment_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນການຈ່າຍຄ່າຮຽນ")
    return obj


def get_registration_with_payment_context(db: Session, registration_id: str) -> Registration:
    obj = db.query(Registration).options(
        joinedload(Registration.student),
        joinedload(Registration.tuition_payments),
    ).filter(Registration.registration_id == registration_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນການລົງທະບຽນ")
    return obj


def build_payment_history_report_request(
    db: Session,
    registration_id: str,
) -> TuitionPaymentHistoryReportRequest:
    registration = get_registration_with_payment_context(db, registration_id)
    if not registration.student:
        raise NotFoundException("ຂໍ້ມູນນັກຮຽນ")

    payments = sorted(
        registration.tuition_payments or [],
        key=lambda item: (item.pay_date, item.tuition_payment_id),
    )
    final_amount = Decimal(registration.final_amount)
    cumulative_paid_amount = Decimal("0")
    payment_items: list[TuitionPaymentHistoryItem] = []

    for installment_index, payment in enumerate(payments, start=1):
        paid_amount = Decimal(payment.paid_amount)
        cumulative_paid_amount += paid_amount
        remaining_amount = max(final_amount - cumulative_paid_amount, Decimal("0"))
        payment_method = (
            payment.payment_method.value
            if hasattr(payment.payment_method, "value")
            else str(payment.payment_method)
        )
        payment_items.append(
            TuitionPaymentHistoryItem(
                installment_index=installment_index,
                invoice_id=payment.tuition_payment_id,
                pay_date=payment.pay_date,
                payment_method=payment_method,
                paid_amount=paid_amount,
                cumulative_paid_amount=cumulative_paid_amount,
                remaining_amount=remaining_amount,
                status="ຈ່າຍແລ້ວ" if remaining_amount <= 0 else "ຈ່າຍບາງສ່ວນ",
            )
        )

    total_paid_amount = cumulative_paid_amount
    remaining_amount = max(final_amount - total_paid_amount, Decimal("0"))

    return TuitionPaymentHistoryReportRequest(
        registration_id=registration.registration_id,
        student_id=registration.student.student_id,
        student_name=f"{registration.student.student_name} {registration.student.student_lastname}",
        registration_date=registration.registration_date,
        total_fee=final_amount,
        total_paid_amount=total_paid_amount,
        remaining_amount=remaining_amount,
        installment_count=len(payment_items),
        payment_items=payment_items,
    )


def build_receipt_request(db: Session, tuition_payment_id: str) -> TuitionPaymentReceiptRequest:
    payment = get_by_id(db, tuition_payment_id)
    registration = payment.registration
    if not registration or not registration.student:
        raise NotFoundException("ຂໍ້ມູນການລົງທະບຽນ")

    payments = db.query(TuitionPayment).filter(
        TuitionPayment.registration_id == registration.registration_id
    ).order_by(TuitionPayment.pay_date.asc(), TuitionPayment.tuition_payment_id.asc()).all()

    payment_ids = [item.tuition_payment_id for item in payments]
    installment_index = payment_ids.index(payment.tuition_payment_id) + 1
    cumulative_paid_amount = sum(
        (Decimal(item.paid_amount) for item in payments[:installment_index]),
        Decimal('0'),
    )
    installment_total = len(payments)

    selected_fees = []
    subject_fee_total = Decimal('0')
    for detail in registration.details or []:
        fee_rel = detail.fee_rel
        subject_detail = fee_rel.subject_detail if fee_rel else None
        subject = subject_detail.subject if subject_detail else None
        level = subject_detail.level if subject_detail else None
        fee_amount = Decimal(fee_rel.fee) if fee_rel and fee_rel.fee is not None else Decimal('0')
        subject_fee_total += fee_amount
        selected_fees.append(
            {
                'subject_name': subject.subject_name if subject else '-',
                'level_name': level.level_name if level else '-',
                'fee': fee_amount,
            }
        )

    total_fee = Decimal(registration.total_amount)
    other_fee_amount = max(total_fee - subject_fee_total, Decimal('0'))
    remaining_amount = max(Decimal(registration.final_amount) - cumulative_paid_amount, Decimal('0'))

    return TuitionPaymentReceiptRequest(
        tuition_payment_id=payment.tuition_payment_id,
        invoice_id=payment.tuition_payment_id,
        registration_id=registration.registration_id,
        student_name=f'{registration.student.student_name} {registration.student.student_lastname}',
        payment_method=payment.payment_method.value if hasattr(payment.payment_method, 'value') else str(payment.payment_method),
        pay_date=payment.pay_date,
        installment_index=installment_index,
        installment_total=installment_total,
        selected_fees=selected_fees,
        other_fee_label='ຄ່າອື່ນໆ',
        other_fee_amount=other_fee_amount,
        total_fee=Decimal(registration.final_amount),
        paid_amount=Decimal(payment.paid_amount),
        cumulative_paid_amount=cumulative_paid_amount,
        remaining_amount=remaining_amount,
    )


def create(db: Session, data: TuitionPaymentCreate):
    tuition_payment_id = generate_payment_id(db)
    obj = TuitionPayment(
        tuition_payment_id=tuition_payment_id,
        **data.model_dump(exclude_none=True)
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    _update_registration_status(db, data.registration_id)
    registration = db.query(Registration).options(
        joinedload(Registration.student)
    ).filter(Registration.registration_id == data.registration_id).first()
    student_fullname = ""
    if registration and registration.student:
        student_fullname = f"{registration.student.student_name} {registration.student.student_lastname}"
    income = Income(
        tuition_payment_id=tuition_payment_id,
        amount=data.paid_amount,
        description=f"ຄ່າຮຽນ: {student_fullname}" if student_fullname else f"ຄ່າຮຽນ: {tuition_payment_id}",
        income_date=data.pay_date if data.pay_date else func.now(),
    )
    db.add(income)
    db.commit()
    # Refresh the payment object to ensure it has latest data including updated registration
    db.refresh(obj)
    return get_by_id(db, tuition_payment_id)


def update(db: Session, tuition_payment_id: str, data: TuitionPaymentUpdate):
    obj = get_by_id(db, tuition_payment_id)
    registration_id = obj.registration_id
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    _update_registration_status(db, registration_id)
    if data.paid_amount is not None:
        income = db.query(Income).filter(
            Income.tuition_payment_id == tuition_payment_id
        ).first()
        if income:
            income.amount = data.paid_amount
            if data.pay_date:
                income.income_date = data.pay_date
            db.commit()
    # Refresh to get updated registration status
    db.refresh(obj)
    return obj


def delete(db: Session, tuition_payment_id: str):
    obj = db.query(TuitionPayment).filter(
        TuitionPayment.tuition_payment_id == tuition_payment_id
    ).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນການຈ່າຍຄ່າຮຽນ")
    registration_id = obj.registration_id
    db.delete(obj)
    db.commit()
    db.expire_all()
    _update_registration_status(db, registration_id)
