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


def _check_duplicate_name(
    db: Session,
    donor_name: str,
    donor_lastname: str,
    exclude_id: str | None = None,
):
    query = db.query(Donor).filter(
        Donor.donor_name == donor_name,
        Donor.donor_lastname == donor_lastname,
    )
    if exclude_id is not None:
        query = query.filter(Donor.donor_id != exclude_id)
    if query.first():
        raise ConflictException(
            f"ຜູ້ບໍລິຈາກຊື່ '{donor_name} {donor_lastname}' ມີຢູ່ແລ້ວ"
        )


def get_all(db: Session):
    return db.query(Donor).all()


def get_by_id(db: Session, donor_id: str):
    obj = db.query(Donor).filter(Donor.donor_id == donor_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນຜູ້ບໍລິຈາກ")
    return obj


def create(db: Session, data: DonorCreate):
    _check_duplicate_name(db, data.donor_name, data.donor_lastname)
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
    if data.donor_name is not None or data.donor_lastname is not None:
        _check_duplicate_name(
            db,
            data.donor_name if data.donor_name is not None else obj.donor_name,
            data.donor_lastname if data.donor_lastname is not None else obj.donor_lastname,
            exclude_id=donor_id,
        )
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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictException("ບໍ່ສາມາດລຶບຜູ້ບໍລິຈາກນີ້ໄດ້ ເນື່ອງຈາກມີຂໍ້ມູນການບໍລິຈາກອ້າງອີງຢູ່")
