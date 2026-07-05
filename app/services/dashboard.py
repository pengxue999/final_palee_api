from sqlalchemy.orm import Session
from sqlalchemy import extract, func
from decimal import Decimal
from app.models.academic_years import AcademicYear
from app.models.student import Student
from app.models.teacher import Teacher
from app.models.teacher_assignment import TeacherAssignment
from app.models.registration import Registration
from app.models.registration_detail import RegistrationDetail
from app.models.fee import Fee
from app.models.income import Income
from app.models.expense import Expense
from app.enums.academic_status import AcademicStatusEnum


def get_active_academic_year(db: Session) -> AcademicYear:
    """ດຶງຂໍ້ມູນສົກຮຽນທີ່ຍັງດຳເນີນການ"""
    return db.query(AcademicYear).filter(
        AcademicYear.status == AcademicStatusEnum.ACTIVE
    ).first()


def get_academic_target_year(db: Session, academic_id: str = None) -> int | None:
    """ແປງສົກຮຽນ 2025-2026 ເປັນປີເປົ້າໝາຍ 2026."""
    if not academic_id:
        return None

    academic_year = db.query(AcademicYear).filter(
        AcademicYear.academic_id == academic_id
    ).first()

    if not academic_year or not academic_year.academic_year:
        return None

    try:
        return int(str(academic_year.academic_year).split('-')[-1].strip())
    except (AttributeError, ValueError):
        return None


def get_student_stats(db: Session, academic_id: str = None) -> dict:
    """
    ດຶງສະຖິຕິນັກຮຽນ
    - total: ຈຳນວນນັກຮຽນທັງໝົດ (ຈາກຕາຕະລາງ Student)
    - active: ຈຳນວນນັກຮຽນທີ່ລົງທະບຽນໃນສົກຮຽນທີ່ລະບຸ
    """
    total = db.query(Student).count()

    active = 0
    if academic_id:
        active = db.query(Registration.student_id).join(
            RegistrationDetail, Registration.registration_id == RegistrationDetail.registration_id
        ).join(
            Fee, RegistrationDetail.fee_id == Fee.fee_id
        ).filter(
            Fee.academic_id == academic_id
        ).distinct().count()

    return {
        "total": total,
        "active": active
    }


def get_teacher_stats(db: Session, academic_id: str = None) -> dict:
    """
    ດຶງສະຖິຕິອາຈານ
    - total: ຈຳນວນອາຈານທັງໝົດ (ຈາກຕາຕະລາງ Teacher)
    - active: ຈຳນວນອາຈານທີ່ມີການມອບໝາຍໃນສົກຮຽນທີ່ລະບຸ
    """
    total = db.query(Teacher).count()

    active = 0
    if academic_id:
        assigned_count = db.query(TeacherAssignment.teacher_id).filter(
            TeacherAssignment.academic_id == academic_id
        ).distinct().count()
        active = assigned_count

    return {
        "total": total,
        "active": active
    }


def get_income_stats(db: Session, academic_id: str = None) -> dict:
    total_income = db.query(func.sum(Income.amount)).scalar() or Decimal('0')

    tuition_income = db.query(func.sum(Income.amount)).filter(
        Income.tuition_payment_id != None
    ).scalar() or Decimal('0')

    donation_income = db.query(func.sum(Income.amount)).filter(
        Income.donation_id != None
    ).scalar() or Decimal('0')

    other_income = float(total_income) - float(tuition_income) - float(donation_income)

    target_year = get_academic_target_year(db, academic_id)
    if target_year is not None:
        total_income = db.query(func.sum(Income.amount)).filter(
            extract('year', Income.income_date) == target_year
        ).scalar() or Decimal('0')
        tuition_income = db.query(func.sum(Income.amount)).filter(
            Income.tuition_payment_id != None,
            extract('year', Income.income_date) == target_year
        ).scalar() or Decimal('0')

        donation_income = db.query(func.sum(Income.amount)).filter(
            Income.donation_id != None,
            extract('year', Income.income_date) == target_year
        ).scalar() or Decimal('0')

        other_income = float(total_income) - float(tuition_income) - float(donation_income)
    return {
        "total": float(total_income),
        "tuition": float(tuition_income),
        "donation": float(donation_income),
        "other": other_income
    }


def get_expense_stats(db: Session, academic_id: str = None) -> dict:
    query = db.query(func.sum(Expense.amount))
    salary_query = db.query(func.sum(Expense.amount)).filter(
        Expense.salary_payment_id != None
    )

    target_year = get_academic_target_year(db, academic_id)
    if target_year is not None:
        query = query.filter(extract('year', Expense.expense_date) == target_year)
        salary_query = salary_query.filter(
            extract('year', Expense.expense_date) == target_year
        )

    total_expense = query.scalar() or Decimal('0')
    salary_expense = salary_query.scalar() or Decimal('0')
    other_expense = float(total_expense) - float(salary_expense)

    return {
        "total": float(total_expense),
        "salary": float(salary_expense),
        "other": other_expense
    }


def get_dashboard_stats(db: Session, academic_id: str = None) -> dict:
    if academic_id:
        academic_year = db.query(AcademicYear).filter(
            AcademicYear.academic_id == academic_id
        ).first()
    else:
        academic_year = get_active_academic_year(db)
        academic_id = academic_year.academic_id if academic_year else None

    return {
        "academic_year": {
            "academic_id": academic_year.academic_id if academic_year else None,
            "academic_year": academic_year.academic_year if academic_year else "ບໍ່ມີສົກຮຽນທີ່ດຳເນີນການ",
            "status": academic_year.status.value if academic_year else None
        },
        "students": get_student_stats(db, academic_id),
        "teachers": get_teacher_stats(db, academic_id),
        "income": get_income_stats(db, academic_id),
        "expenses": get_expense_stats(db, academic_id),
        "balance": get_income_stats(db, academic_id)["total"] - get_expense_stats(db, academic_id)["total"]
    }
