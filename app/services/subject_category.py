from sqlalchemy.orm import Session
from app.models.subject_category import SubjectCategory
from app.schemas.subject_category import SubjectCategoryCreate, SubjectCategoryUpdate
from app.configs.exceptions import ConflictException, NotFoundException
from sqlalchemy.exc import IntegrityError
from app.utils.foreign_key_helper import safe_delete_with_constraint_check


def _generate_subject_category_id(db: Session) -> str:
    last_subject_category = db.query(SubjectCategory).order_by(SubjectCategory.subject_category_id.desc()).first()
    if not last_subject_category:
        return "SC001"
    last_id = last_subject_category.subject_category_id
    if last_id.startswith("SC") and last_id[2:].isdigit():
        num = int(last_id[2:]) + 1
        return f"SC{num:03d}"
    return "SC001"

def get_all(db: Session):
    return db.query(SubjectCategory).all()


def get_by_id(db: Session, subject_category_id: str) -> SubjectCategory:
    obj = db.query(SubjectCategory).filter(SubjectCategory.subject_category_id == subject_category_id).first()
    if not obj:
        raise NotFoundException("ໝວດວິຊາ")
    return obj


def create(db: Session, data: SubjectCategoryCreate):
    subject_category_id= _generate_subject_category_id(db)
    obj = SubjectCategory(subject_category_id=subject_category_id, **data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ໝວດວິຊາ '{data.subject_category_name}' ມີຢູ່ແລ້ວ")


def update(db: Session, subject_category_id: str, data: SubjectCategoryUpdate):
    obj = get_by_id(db, subject_category_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ໝວດວິຊາ '{data.subject_category_name}' ມີຢູ່ແລ້ວ")


def delete(db: Session, subject_category_id: str):
    obj = get_by_id(db, subject_category_id)
    safe_delete_with_constraint_check(db, obj, "subject_category")
