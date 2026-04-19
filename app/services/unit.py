from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.unit import Unit
from app.schemas.unit import UnitCreate, UnitUpdate
from app.configs.exceptions import NotFoundException, ConflictException


def get_all(db: Session):
    return db.query(Unit).all()

def get_by_id(db: Session, unit_id: int) -> Unit:
    obj = db.query(Unit).filter(Unit.unit_id == unit_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນຫົວໜ່ວຍ")
    return obj

def create(db: Session, data: UnitCreate) -> Unit:
    obj = Unit(**data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ຫົວໜ່ວຍ '{data.unit_name}' ມີຢູ່ແລ້ວ")

def update(db: Session, unit_id: int, data: UnitUpdate) -> Unit:
    obj = get_by_id(db, unit_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ຫົວໜ່ວຍ '{data.unit_name}' ມີຢູ່ແລ້ວ")

def delete(db: Session, unit_id: int):
    obj = get_by_id(db, unit_id)
    db.delete(obj)
    db.commit()
