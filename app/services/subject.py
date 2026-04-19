from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.configs.exceptions import ConflictException, NotFoundException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check

def _generate_subject_id(db: Session) -> str:
    last_subject = db.query(Subject).order_by(Subject.subject_id.desc()).first()
    if not last_subject:
        return "S001"
    last_id = last_subject.subject_id
    if last_id.startswith("S") and last_id[2:].isdigit():
        num = int(last_id[2:]) + 1
        return f"S{num:03d}"
    return "S001"
def get_all(db: Session):
    return db.query(Subject).options(joinedload(Subject.category)).all()


def get_by_id(db: Session, subject_id: str) -> Subject:
    obj = db.query(Subject).options(joinedload(Subject.category)).filter(Subject.subject_id == subject_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນວິຊາ")
    return obj


def create(db: Session, data: SubjectCreate):
    subject_id= _generate_subject_id(db)
    obj = Subject(subject_id=subject_id, **data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ວິຊາ '{data.subject_name}' ມີຢູ່ແລ້ວ")


def update(db: Session, subject_id: str, data: SubjectUpdate):
    obj = get_by_id(db, subject_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ວິຊາ '{data.subject_name}' ມີຢູ່ແລ້ວ")


def delete(db: Session, subject_id: str):
    obj = get_by_id(db, subject_id)
    safe_delete_with_constraint_check(db, obj, "subject")
