from sqlalchemy.orm import Session
from app.models.province import Province
from app.schemas.province import ProvinceCreate, ProvinceUpdate
from app.configs.exceptions import NotFoundException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check


def get_all(db: Session):
    return db.query(Province).all()


def get_by_id(db: Session, province_id: int) -> Province:
    obj = db.query(Province).filter(Province.province_id == province_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນແຂວງ")
    return obj


def create(db: Session, data: ProvinceCreate):
    obj = Province(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, province_id: int, data: ProvinceUpdate):
    obj = get_by_id(db, province_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, province_id: int):
    obj = get_by_id(db, province_id)
    safe_delete_with_constraint_check(db, obj, "province")
