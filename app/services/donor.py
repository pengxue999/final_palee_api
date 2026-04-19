from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models.donor import Donor
from app.schemas.donor import DonorCreate, DonorUpdate
from app.configs.exceptions import ConflictException, NotFoundException

def _generate_donor_id(db: Session) -> str:
    last_donor = (
        db.query(Donor)
        .order_by(
            func.length(Donor.donor_id).desc(),
            Donor.donor_id.desc()
        )
        .first()
    )
    if not last_donor:
        return "DN001"
    last_id = last_donor.donor_id
    if last_id.startswith("DN") and last_id[2:].isdigit():
        num = int(last_id[2:]) + 1
        return f"DN{num:03d}"
    return "DN001"

def get_all(db: Session):
    return db.query(Donor).all()


def get_by_id(db: Session, donor_id: str):
    obj = db.query(Donor).filter(Donor.donor_id == donor_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນຜູ້ບໍລິຈາກ")
    return obj


def create(db: Session, data: DonorCreate):
    donor_id= _generate_donor_id(db)
    obj = Donor(donor_id=donor_id, **data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ເບີໂທລະສັບນີ້ '{data.donor_contact}' ມີຢູ່ແລ້ວ")


def update(db: Session, donor_id: str, data: DonorUpdate):
    obj = get_by_id(db, donor_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ເບີໂທລະສັບນີ້ '{data.donor_contact}' ມີຢູ່ແລ້ວ")


def delete(db: Session, donor_id: str):
    obj = get_by_id(db, donor_id)
    db.delete(obj)
    db.commit()
