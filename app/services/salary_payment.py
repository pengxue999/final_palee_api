from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, extract, and_
from datetime import datetime, date
from decimal import Decimal
import calendar
import re
from app.models.salary_payment import SalaryPayment
from app.models.teaching_log import TeachingLog
from app.models.teacher_assignment import TeacherAssignment
from app.models.teacher import Teacher
from app.models.expense import Expense
from app.models.expense_category import ExpenseCategory
from app.schemas.salary_payment import (
    SalaryPaymentCreate,
    SalaryPaymentUpdate,
    SalaryPaymentReceiptRequest,
)
from app.configs.exceptions import NotFoundException


SALARY_CATEGORY_NAME = 'ຄ່າສອນ'
MONTH_NAMES = {
    1: 'ມັງກອນ',
    2: 'ກຸມພາ',
    3: 'ມີນາ',
    4: 'ເມສາ',
    5: 'ພຶດສະພາ',
    6: 'ມິຖຸນາ',
    7: 'ກໍລະກົດ',
    8: 'ສິງຫາ',
    9: 'ກັນຍາ',
    10: 'ຕຸລາ',
    11: 'ພະຈິກ',
    12: 'ທັນວາ',
}


def _get_or_create_salary_category(db: Session) -> int:
    """Get or create the salary expense category ('ຄ່າສອນ')."""
    category = db.query(ExpenseCategory).filter(
        ExpenseCategory.expense_category == SALARY_CATEGORY_NAME
    ).first()

    if category:
        return category.expense_category_id

    new_category = ExpenseCategory(expense_category=SALARY_CATEGORY_NAME)
    db.add(new_category)
    db.flush()
    return new_category.expense_category_id


def _month_label(month: int) -> str:
    return MONTH_NAMES.get(month, str(month))


def generate_salary_payment_id(db: Session) -> str:
    """Generate sequential payment ID in format SPT0001, SPT0002, etc."""
    latest = db.query(SalaryPayment).order_by(
        func.length(SalaryPayment.salary_payment_id).desc(),
        SalaryPayment.salary_payment_id.desc()
    ).first()

    if latest and latest.salary_payment_id:
        match = re.match(r'SPT(\d+)', latest.salary_payment_id)
        if match:
            next_num = int(match.group(1)) + 1
        else:
            next_num = 1
    else:
        next_num = 1

    return f'SPT{next_num:04d}'


def _month_date_range(year: int, month: int):
    """Return (from_date_str, to_date_str) for the full calendar month."""
    last_day = calendar.monthrange(year, month)[1]
    return f"{year}-{month:02d}-01", f"{year}-{month:02d}-{last_day:02d}"


def _compute_actual_amount(db: Session, teacher_id: str, year: int, month: int):
    """Actual earned = attended sessions (ຂຶ້ນສອນ) × hourly_rate for the month."""
    from_date, to_date = _month_date_range(year, month)
    row = db.query(
        func.coalesce(func.sum(TeachingLog.hourly), 0).label('total_hours'),
        func.coalesce(
            func.sum(TeachingLog.hourly * TeacherAssignment.hourly_rate), 0
        ).label('total_amount'),
        func.count(TeachingLog.teaching_log_id).label('total_sessions'),
    ).join(
        TeacherAssignment, TeachingLog.assignment_id == TeacherAssignment.assignment_id
    ).filter(
        TeacherAssignment.teacher_id == teacher_id,
        TeachingLog.status == 'ຂຶ້ນສອນ',
        func.date(TeachingLog.teaching_date) >= from_date,
        func.date(TeachingLog.teaching_date) <= to_date,
    ).first()
    return {
        'total_hours': float(row.total_hours or 0),
        'total_amount': float(row.total_amount or 0),
        'total_sessions': int(row.total_sessions or 0),
    }


def _compute_planned_amount(db: Session, teacher_id: str, year: int, month: int):
    """Planned = all scheduled sessions (ຂຶ້ນສອນ + ຂາດສອນ) × hourly_rate for the month."""
    from_date, to_date = _month_date_range(year, month)
    row = db.query(
        func.coalesce(func.sum(TeachingLog.hourly), 0).label('total_hours'),
        func.coalesce(
            func.sum(TeachingLog.hourly * TeacherAssignment.hourly_rate), 0
        ).label('total_amount'),
    ).join(
        TeacherAssignment, TeachingLog.assignment_id == TeacherAssignment.assignment_id
    ).filter(
        TeacherAssignment.teacher_id == teacher_id,
        func.date(TeachingLog.teaching_date) >= from_date,
        func.date(TeachingLog.teaching_date) <= to_date,
    ).first()
    return {
        'planned_hours': float(row.total_hours or 0),
        'planned_amount': float(row.total_amount or 0),
    }


def _compute_total_paid(db: Session, teacher_id: str, year: int, month: int) -> float:
    """Sum of all payments for (teacher_id, year, month)."""
    row = db.query(
        func.coalesce(func.sum(SalaryPayment.total_amount), 0).label('total_paid')
    ).filter(
        SalaryPayment.teacher_id == teacher_id,
        extract('year', SalaryPayment.payment_date) == year,
        SalaryPayment.month == month,
    ).first()
    return float(row.total_paid or 0)


def _compute_prior_debt(db: Session, teacher_id: str, year: int, month: int) -> float:
    """Cumulative net balance from all months BEFORE (year, month).

    For each prior month: net = actual_earned - total_paid
    Sum of all prior nets.  Negative value means teacher was overpaid (advance
    exceeded actual) and that debt carries forward into the current month.
    """
    year_col = extract('year', SalaryPayment.payment_date).label('y')
    month_col = extract('month', SalaryPayment.payment_date).label('m')
    prior_months = db.query(
        year_col,
        SalaryPayment.month.label('m'),
        func.sum(SalaryPayment.total_amount).label('total_paid'),
    ).filter(
        SalaryPayment.teacher_id == teacher_id,
        (year_col * 100 + SalaryPayment.month) < (year * 100 + month),
    ).group_by(year_col, SalaryPayment.month).all()

    cumulative = 0.0
    for row in prior_months:
        actual = _compute_actual_amount(db, teacher_id, int(row.y), int(row.m))
        cumulative += actual['total_amount'] - float(row.total_paid)

    return cumulative


def get_all(db: Session, teacher_id: str = None, year: int = None, month: int = None):
    query = db.query(SalaryPayment).options(
        joinedload(SalaryPayment.teacher),
        joinedload(SalaryPayment.user),
    )
    if teacher_id:
        query = query.filter(SalaryPayment.teacher_id == teacher_id)
    if year:
        query = query.filter(extract('year', SalaryPayment.payment_date) == year)
    if month:
        query = query.filter(SalaryPayment.month == month)
    return query.order_by(SalaryPayment.payment_date.desc()).all()


def get_by_id(db: Session, salary_payment_id: str) -> SalaryPayment:
    obj = db.query(SalaryPayment).options(
        joinedload(SalaryPayment.teacher),
        joinedload(SalaryPayment.user),
    ).filter(SalaryPayment.salary_payment_id == salary_payment_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນການຈ່າຍເງິນສອນ")
    return obj


def get_by_teacher(db: Session, teacher_id: str):
    """Get all payments for a specific teacher ordered newest first."""
    return db.query(SalaryPayment).options(
        joinedload(SalaryPayment.teacher),
        joinedload(SalaryPayment.user),
    ).filter(
        SalaryPayment.teacher_id == teacher_id
    ).order_by(SalaryPayment.payment_date.desc()).all()


def get_teaching_months(db: Session, teacher_id: str = None):
    """Get distinct (year, month) pairs from teaching_log."""
    year_col = extract('year', TeachingLog.teaching_date).label('year')
    month_col = extract('month', TeachingLog.teaching_date).label('month')

    query = db.query(
        year_col,
        month_col,
        func.count(TeachingLog.teaching_log_id).label('count'),
    ).filter(TeachingLog.status == 'ຂຶ້ນສອນ')

    if teacher_id:
        query = query.join(
            TeacherAssignment,
            TeachingLog.assignment_id == TeacherAssignment.assignment_id,
        ).filter(TeacherAssignment.teacher_id == teacher_id)

    results = query.group_by(
        year_col, month_col
    ).order_by(year_col.desc(), month_col.desc()).all()

    month_names = [
        '', 'ມັງກອນ', 'ກຸມພາ', 'ມີນາ', 'ເມສາ', 'ພຶດສະພາ', 'ມິຖຸນາ',
        'ກໍລະກົດ', 'ສິງຫາ', 'ກັນຍາ', 'ຕຸລາ', 'ພະຈິກ', 'ທັນວາ',
    ]
    return [
        {
            'year': int(r.year),
            'month': int(r.month),
            'label': f"{month_names[int(r.month)]} {int(r.year)}",
            'count': r.count,
        }
        for r in results
    ]


def calculate_teacher_salary(db: Session, teacher_id: str, year: int, month: int):
    actual = _compute_actual_amount(db, teacher_id, year, month)
    planned = _compute_planned_amount(db, teacher_id, year, month)
    total_paid = _compute_total_paid(db, teacher_id, year, month)
    prior_debt = _compute_prior_debt(db, teacher_id, year, month)

    remaining = actual['total_amount'] + prior_debt - total_paid

    teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    assignment = db.query(TeacherAssignment).filter(
        TeacherAssignment.teacher_id == teacher_id
    ).first()
    hourly_rate = float(assignment.hourly_rate) if assignment else 0.0

    return {
        'teacher_id': teacher_id,
        'teacher_name': teacher.teacher_name if teacher else '',
        'teacher_lastname': teacher.teacher_lastname if teacher else '',
        'year': year,
        'month': month,
        'total_hours': actual['total_hours'],
        'total_amount': actual['total_amount'],
        'planned_hours': planned['planned_hours'],
        'planned_amount': planned['planned_amount'],
        'hourly_rate': hourly_rate,
        'total_sessions': actual['total_sessions'],
        'total_paid': total_paid,
        'prior_debt': prior_debt,
        'remaining_balance': max(remaining, 0),
    }


def get_monthly_teachers_summary(db: Session, year: int, month: int):
    """All teachers that have any teaching log in year/month, with their salary summary."""
    from_date, to_date = _month_date_range(year, month)

    teacher_ids_q = db.query(TeacherAssignment.teacher_id).join(
        TeachingLog, TeachingLog.assignment_id == TeacherAssignment.assignment_id
    ).filter(
        func.date(TeachingLog.teaching_date) >= from_date,
        func.date(TeachingLog.teaching_date) <= to_date,
    ).distinct().all()

    return [
        calculate_teacher_salary(db, row.teacher_id, year, month)
        for row in teacher_ids_q
    ]


def get_payment_summary_by_teacher(db: Session, teacher_id: str, year: int, month: int):
    """Payment summary for a teacher in a specific month."""
    data = calculate_teacher_salary(db, teacher_id, year, month)
    return {
        'teacher_id': teacher_id,
        'year': year,
        'month': month,
        'expected_amount': data['total_amount'],
        'planned_amount': data['planned_amount'],
        'total_hours': data['total_hours'],
        'hourly_rate': data['hourly_rate'],
        'total_paid': data['total_paid'],
        'prior_debt': data['prior_debt'],
        'remaining_balance': data['remaining_balance'],
        'is_fully_paid': data['remaining_balance'] <= 0,
    }


def build_receipt_request(db: Session, salary_payment_id: str) -> SalaryPaymentReceiptRequest:
    payment = get_by_id(db, salary_payment_id)
    year = payment.payment_date.year
    month = payment.month

    payments = db.query(SalaryPayment).filter(
        SalaryPayment.teacher_id == payment.teacher_id,
        extract('year', SalaryPayment.payment_date) == year,
        SalaryPayment.month == month,
    ).order_by(SalaryPayment.payment_date.asc(), SalaryPayment.salary_payment_id.asc()).all()

    payment_ids = [item.salary_payment_id for item in payments]
    installment_index = payment_ids.index(payment.salary_payment_id) + 1
    cumulative_paid_amount = sum(
        (Decimal(item.total_amount) for item in payments[:installment_index]),
        Decimal('0'),
    )
    outstanding_before_payment = sum(
        (Decimal(item.total_amount) for item in payments[:installment_index - 1]),
        Decimal('0'),
    )

    calculation = calculate_teacher_salary(db, payment.teacher_id, year, month)
    expected_amount = Decimal(str(calculation['total_amount']))
    prior_debt = Decimal(str(calculation['prior_debt']))
    due_before_payment = max(
        expected_amount + prior_debt - outstanding_before_payment,
        Decimal('0'),
    )
    remaining_amount = max(
        expected_amount + prior_debt - cumulative_paid_amount,
        Decimal('0'),
    )
    teacher_name = f"{payment.teacher.teacher_name} {payment.teacher.teacher_lastname}".strip()

    return SalaryPaymentReceiptRequest(
        salary_payment_id=payment.salary_payment_id,
        invoice_id=payment.salary_payment_id,
        teacher_id=payment.teacher_id,
        teacher_name=teacher_name or payment.teacher_id,
        user_name=payment.user.user_name if payment.user else '-',
        pay_date=payment.payment_date,
        month=month,
        month_label=_month_label(month),
        year=year,
        installment_index=installment_index,
        installment_total=len(payments),
        total_hours=float(calculation['total_hours']),
        hourly_rate=Decimal(str(calculation['hourly_rate'])),
        expected_amount=expected_amount,
        prior_debt=prior_debt,
        outstanding_before_payment=due_before_payment,
        paid_amount=Decimal(payment.total_amount),
        cumulative_paid_amount=cumulative_paid_amount,
        remaining_amount=remaining_amount,
        status='ຈ່າຍແລ້ວ' if remaining_amount <= 0 else payment.status,
    )


def create(db: Session, data: SalaryPaymentCreate):
    salary_payment_id = data.salary_payment_id or generate_salary_payment_id(db)

    payment = SalaryPayment(
        salary_payment_id=salary_payment_id,
        **data.model_dump(exclude={'salary_payment_id'})
    )
    db.add(payment)
    db.flush()

    teacher = db.query(Teacher).filter(Teacher.teacher_id == data.teacher_id).first()
    teacher_fullname = ""
    if teacher:
        teacher_fullname = f"{teacher.teacher_name} {teacher.teacher_lastname}"

    category_id = _get_or_create_salary_category(db)
    expense = Expense(
        expense_category_id=category_id,
        salary_payment_id=payment.salary_payment_id,
        amount=payment.total_amount,
        description=f'ຈ່າຍເງິນສອນ: {teacher_fullname}' if teacher_fullname else f'ຈ່າຍເງິນສອນ: {payment.salary_payment_id}',
        expense_date=payment.payment_date,
    )
    db.add(expense)
    db.commit()
    db.refresh(payment)
    return payment


def update(db: Session, salary_payment_id: str, data: SalaryPaymentUpdate):
    payment = get_by_id(db, salary_payment_id)

    for field, value in data.model_dump(exclude_none=True).items():
        setattr(payment, field, value)

    if data.total_amount is not None:
        expense = db.query(Expense).filter(
            Expense.salary_payment_id == salary_payment_id
        ).first()
        if expense:
            expense.amount = data.total_amount

    db.commit()
    db.refresh(payment)
    return payment


def delete(db: Session, salary_payment_id: str):
    payment = get_by_id(db, salary_payment_id)
    db.delete(payment)
    db.commit()

