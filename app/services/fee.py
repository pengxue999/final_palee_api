from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from app.models.fee import Fee
from app.models.subject_detail import SubjectDetail
from app.models.subject import Subject
from app.schemas.fee import FeeCreate, FeeUpdate
from app.configs.exceptions import ConflictException

def _generate_fee_id(db: Session) -> str:
    last_fee = db.query(Fee).order_by(Fee.fee_id.desc()).first()
    if not last_fee:
        return "F001"
    last_id = last_fee.fee_id
    if last_id.startswith("F") and last_id[1:].isdigit():
        num = int(last_id[1:]) + 1
        return f"F{num:03d}"
    return "F001"

def _fee_options():
    return [
        joinedload(Fee.subject_detail).joinedload(SubjectDetail.subject).joinedload(Subject.category),
        joinedload(Fee.subject_detail).joinedload(SubjectDetail.level),
        joinedload(Fee.academic_year),
    ]

def get_all(db: Session):
    return db.query(Fee).options(*_fee_options()).all()

def get_by_id(db: Session, fee_id: str) -> Fee:
    obj = db.query(Fee).options(*_fee_options()).filter(Fee.fee_id == fee_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນຄ່າຮຽນ")
    return obj

def create(db: Session, data: FeeCreate):
    fee_id = _generate_fee_id(db)
    obj = Fee(
        fee_id=fee_id,
        subject_detail_id=data.subject_detail_id,
        academic_id=data.academic_id,
        fee=data.fee
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictException("ຄ່າຮຽນຂອງວິຊາ/ລະດັບ/ສົກຮຽນນີ້ມີຢູ່ແລ້ວ")
    db.refresh(obj)
    return get_by_id(db, fee_id)

def update(db: Session, fee_id: str, data: FeeUpdate):
    obj = get_by_id(db, fee_id)
    if data.subject_detail_id is not None:
        obj.subject_detail_id = data.subject_detail_id
    if data.academic_id is not None:
        obj.academic_id = data.academic_id
    if data.fee is not None:
        obj.fee = data.fee
    db.commit()
    return get_by_id(db, fee_id)

def delete(db: Session, fee_id: str):
    obj = get_by_id(db, fee_id)
    db.delete(obj)
    db.commit()
