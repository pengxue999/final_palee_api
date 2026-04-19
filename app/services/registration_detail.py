from sqlalchemy.orm import Session
from app.models.registration_detail import RegistrationDetail
from app.schemas.registration_detail import RegistrationDetailCreate, RegistrationDetailUpdate
from app.configs.exceptions import NotFoundException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check


def get_all(db: Session):
    return db.query(RegistrationDetail).all()


def get_by_id(db: Session, regis_detail_id: int):
    obj = db.query(RegistrationDetail).filter(RegistrationDetail.regis_detail_id == regis_detail_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນລາຍລະອຽດການລົງທະບຽນ")
    return obj


def create(db: Session, data: RegistrationDetailCreate):
    obj = RegistrationDetail(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, regis_detail_id: int, data: RegistrationDetailUpdate):
    obj = get_by_id(db, regis_detail_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, regis_detail_id: int):
    obj = get_by_id(db, regis_detail_id)
    safe_delete_with_constraint_check(db, obj, "registration_detail")
