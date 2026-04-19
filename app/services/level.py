from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.level import Level
from app.schemas.level import LevelCreate, LevelUpdate
from app.configs.exceptions import ConflictException, NotFoundException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check

def _generate_level_id(db: Session) -> str:
    last_level = db.query(Level).order_by(Level.level_id.desc()).first()
    if not last_level:
        return "L001"
    last_id = last_level.level_id
    if last_id.startswith("L") and last_id[1:].isdigit():
        num = int(last_id[1:]) + 1
        return f"L{num:03d}"
    return "L001"

def get_all(db: Session):
    return db.query(Level).all()

def get_by_id(db: Session, level_id: str) -> Level:
    obj = db.query(Level).filter(Level.level_id == level_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນລະດັບ/ຊັ້ນຮຽນ")
    return obj

def create(db: Session, data: LevelCreate):
    level_id= _generate_level_id(db)
    obj = Level(level_id=level_id, **data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ລະດັບ/ຊັ້ນຮຽນ '{data.level_name}' ມີຢູ່ແລ້ວ")


def update(db: Session, level_id: str, data: LevelUpdate):

    obj = get_by_id(db, level_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ລະດັບ/ຊັ້ນຮຽນ '{data.level_name}' ມີຢູ່ແລ້ວ")


def delete(db: Session, level_id: str):
    obj = get_by_id(db, level_id)
    safe_delete_with_constraint_check(db, obj, "level")
