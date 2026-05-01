from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.configs.exceptions import ConflictException, NotFoundException
from app.models.donation_category import DonationCategory
from app.schemas.donation_category import DonationCategoryCreate, DonationCategoryUpdate


def get_all(db: Session):
    return db.query(DonationCategory).order_by(DonationCategory.donation_category_id.asc()).all()


def get_by_id(db: Session, donation_category_id: int) -> DonationCategory:
    obj = db.query(DonationCategory).filter(
        DonationCategory.donation_category_id == donation_category_id
    ).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນປະເພດການບໍລິຈາກ")
    return obj


def create(db: Session, data: DonationCategoryCreate) -> DonationCategory:
    obj = DonationCategory(**data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(
            f"ປະເພດການບໍລິຈາກ '{data.donation_category_name}' ມີຢູ່ແລ້ວ"
        )


def update(
    db: Session,
    donation_category_id: int,
    data: DonationCategoryUpdate,
) -> DonationCategory:
    obj = get_by_id(db, donation_category_id)
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(
            f"ປະເພດການບໍລິຈາກ '{data.donation_category_name}' ມີຢູ່ແລ້ວ"
        )


def delete(db: Session, donation_category_id: int):
    obj = get_by_id(db, donation_category_id)
    db.delete(obj)
    db.commit()