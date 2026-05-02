from sqlalchemy.orm import Session
from app.models.academic_years import AcademicYear
from app.schemas.academic_years import AcademicYearCreate, AcademicYearUpdate
from app.configs.exceptions import NotFoundException, ConflictException
from sqlalchemy.exc import IntegrityError
from app.utils.foreign_key_helper import safe_delete_with_constraint_check


ACTIVE_ACADEMIC_STATUS = "ACTIVE"


def _generate_academic_id(db: Session) -> str:
    last_academic = db.query(AcademicYear).order_by(AcademicYear.academic_id.desc()).first()
    if not last_academic:
        return "AY001"
    last_id = last_academic.academic_id
    if last_id.startswith("AY") and last_id[2:].isdigit():
        num = int(last_id[2:]) + 1
        return f"AY{num:03d}"
    return "AY001"


def _has_active_academic_year(db: Session, exclude_academic_id: str | None = None) -> bool:
    query = db.query(AcademicYear).filter(AcademicYear.status == ACTIVE_ACADEMIC_STATUS)
    if exclude_academic_id:
        query = query.filter(AcademicYear.academic_id != exclude_academic_id)
    return query.first() is not None


def get_all(db: Session):
    return db.query(AcademicYear).all()


def get_by_id(db: Session, academic_id: str) -> AcademicYear:
    obj = db.query(AcademicYear).filter(AcademicYear.academic_id == academic_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນສົກຮຽນ")
    return obj

def create(db: Session, data: AcademicYearCreate):
    if _has_active_academic_year(db):
        raise ConflictException(
            "ບໍ່ສາມາດເພີ່ມສົກຮຽນໃໝ່ໄດ້ ເນື່ອງຈາກຍັງມີສົກຮຽນທີ່ດໍາເນີນການຢູ່"
        )
    academic_id = _generate_academic_id(db)
    obj = AcademicYear(academic_id=academic_id, **data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ສົກຮຽນ '{data.academic_year}' ມີຢູ່ແລ້ວ")

def update(db: Session, academic_id: str, data: AcademicYearUpdate):
    obj = get_by_id(db, academic_id)
    if (
        data.status == ACTIVE_ACADEMIC_STATUS and
        _has_active_academic_year(db, exclude_academic_id=academic_id)
    ):
        raise ConflictException(
            "ບໍ່ສາມາດປ່ຽນເປັນສົກຮຽນດໍາເນີນການໄດ້ ເນື່ອງຈາກມີສົກຮຽນດໍາເນີນການຢູ່ແລ້ວ"
        )
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ສົກຮຽນ '{data.academic_year}' ມີຢູ່ແລ້ວ")


def delete(db: Session, academic_id: str):
    obj = get_by_id(db, academic_id)
    safe_delete_with_constraint_check(db, obj, "academic_years")
