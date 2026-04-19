from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from app.models.subject_detail import SubjectDetail
from app.models.subject import Subject
from app.models.level import Level
from app.schemas.subject_detail import SubjectDetailCreate, SubjectDetailUpdate
from app.configs.exceptions import NotFoundException, ForeignKeyConstraintException


def _generate_subject_detail_id(db: Session) -> str:
    last_detail = db.query(SubjectDetail).order_by(SubjectDetail.subject_detail_id.desc()).first()
    if not last_detail:
        return "SD001"
    last_id = last_detail.subject_detail_id
    if last_id.startswith("SD") and last_id[2:].isdigit():
        num = int(last_id[2:]) + 1
        return f"SD{num:03d}"
    return "SD001"


def _query_with_relations(db: Session):
    return db.query(SubjectDetail).options(
        joinedload(SubjectDetail.subject),
        joinedload(SubjectDetail.level),
    )


def get_all(db: Session) -> List[SubjectDetail]:
    return _query_with_relations(db).all()


def get_by_id(db: Session, subject_detail_id: str) -> SubjectDetail:
    obj = _query_with_relations(db).filter(
        SubjectDetail.subject_detail_id == subject_detail_id
    ).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນລາຍລະອຽດວິຊາ")
    return obj


def create(db: Session, subject_detail_data: SubjectDetailCreate) -> SubjectDetail:
    from sqlalchemy.exc import IntegrityError

    subject = db.query(Subject).filter(Subject.subject_id == subject_detail_data.subject_id).first()
    if not subject:
        raise NotFoundException(f"ບໍ່ພົບຂໍ້ມູນວິຊາທີ່ມີ ID: {subject_detail_data.subject_id}")

    level = db.query(Level).filter(Level.level_id == subject_detail_data.level_id).first()
    if not level:
        raise NotFoundException(f"ບໍ່ພົບຂໍ້ມູນລະດັບທີ່ມີ ID: {subject_detail_data.level_id}")

    existing = db.query(SubjectDetail).filter(
        SubjectDetail.subject_id == subject_detail_data.subject_id,
        SubjectDetail.level_id == subject_detail_data.level_id
    ).first()
    if existing:
        raise NotFoundException("ວິຊານີ້ຖືກກຳນົດໃຫ້ຂັ້ນຊັ້ນນີ້ແລ້ວ")

    try:
        subject_detail_id = _generate_subject_detail_id(db)
        db_obj = SubjectDetail(
            subject_detail_id=subject_detail_id,
            subject_id=subject_detail_data.subject_id,
            level_id=subject_detail_data.level_id,
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return get_by_id(db, subject_detail_id)
    except IntegrityError:
        db.rollback()
        raise ForeignKeyConstraintException(
            "ບໍ່ສາມາດເພີ່ມລາຍລະອຽດວິຊານີ້ໄດ້ ເນື່ອງຈາກມີຂໍ້ມູນທີ່ເຊື່ອມໂຍງກັນ"
        )


def update(db: Session, subject_detail_id: str, subject_detail_data: SubjectDetailUpdate) -> SubjectDetail:
    db_obj = get_by_id(db, subject_detail_id)
    for field, value in subject_detail_data.model_dump(exclude_none=True).items():
        setattr(db_obj, field, value)
    db.commit()
    db.refresh(db_obj)
    return get_by_id(db, subject_detail_id)


def delete(db: Session, subject_detail_id: str):
    from sqlalchemy.exc import IntegrityError

    db_obj = get_by_id(db, subject_detail_id)
    try:
        db.delete(db_obj)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ForeignKeyConstraintException(
            "ບໍ່ສາມາດລຶບລາຍລະອຽດວິຊານີ້ໄດ້ ເນື່ອງຈາກມີຂໍ້ມູນທີ່ເຊື່ອມໂຍງກັນ"
        )
