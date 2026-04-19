from sqlalchemy.orm import Session, joinedload
from app.models.district import District
from app.schemas.district import DistrictCreate, DistrictUpdate
from app.configs.exceptions import NotFoundException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check


def get_all(db: Session):
    return db.query(District).options(joinedload(District.province)).all()


def get_by_id(db: Session, district_id: int) -> District:
    obj = db.query(District).options(joinedload(District.province)).filter(District.district_id == district_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນເມືອງ")
    return obj


def create(db: Session, data: DistrictCreate):
    obj = District(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, district_id: int, data: DistrictUpdate):
    obj = get_by_id(db, district_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, district_id: int):
    obj = get_by_id(db, district_id)
    safe_delete_with_constraint_check(db, obj, "district")


def get_by_province_id(db: Session, province_id: int):
    return db.query(District).filter(District.province_id == province_id).all()
