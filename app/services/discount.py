from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.discount import Discount
from app.schemas.discount import DiscountCreate, DiscountUpdate
from app.configs.exceptions import NotFoundException, ConflictException
from app.enums.discount_description import DiscountDescriptionEnum


def _generate_discount_id(db: Session) -> str:
    last_discount = db.query(Discount).order_by(Discount.discount_id.desc()).first()
    if not last_discount:
        return "D001"
    last_id = last_discount.discount_id
    if last_id.startswith("D") and last_id[1:].isdigit():
        num = int(last_id[1:]) + 1
        return f"D{num:03d}"
    return "D001"

def get_all(db: Session):
    return db.query(Discount).all()


def get_by_id(db: Session, discount_id: str) -> Discount:
    obj = db.query(Discount).filter(Discount.discount_id == discount_id).first()
    if not obj:
        raise NotFoundException("ສ່ວນຫຼຸດ")
    return obj


def create(db: Session, data: DiscountCreate):
    desc_enum = DiscountDescriptionEnum(data.discount_description)
    existing = db.query(Discount).filter(
        Discount.academic_id == data.academic_id,
        Discount.discount_description == desc_enum.value,
    ).first()
    if existing:
        raise ConflictException("ສ່ວນຫຼຸດນີ້ມີຢູ່ແລ້ວໃນສົກຮຽນນີ້")
    discount_id = _generate_discount_id(db)
    obj = Discount(
        discount_id=discount_id,
        academic_id=data.academic_id,
        discount_amount=data.discount_amount,
        discount_description=desc_enum.value
    )
    db.add(obj)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictException("ສ່ວນຫຼຸດນີ້ມີຢູ່ແລ້ວໃນສົກຮຽນນີ້")
    db.refresh(obj)
    return obj


def _ensure_unique_discount(
    db: Session,
    academic_id: str,
    discount_description: str,
    *,
    exclude_discount_id: str | None = None,
):
    query = db.query(Discount).filter(
        Discount.academic_id == academic_id,
        Discount.discount_description == discount_description,
    )
    if exclude_discount_id is not None:
        query = query.filter(Discount.discount_id != exclude_discount_id)
    if query.first():
        raise ConflictException("ສ່ວນຫຼຸດນີ້ມີຢູ່ແລ້ວໃນສົກຮຽນນີ້")


def update(db: Session, discount_id: str, data: DiscountUpdate):
    obj = get_by_id(db, discount_id)
    update_data = data.model_dump(exclude_none=True)
    if 'discount_description' in update_data:
        update_data['discount_description'] = DiscountDescriptionEnum(update_data['discount_description']).value

    next_academic_id = update_data.get('academic_id', obj.academic_id)
    next_discount_description = update_data.get(
        'discount_description',
        obj.discount_description,
    )
    _ensure_unique_discount(
        db,
        next_academic_id,
        next_discount_description,
        exclude_discount_id=discount_id,
    )

    for field, value in update_data.items():
        setattr(obj, field, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictException("ສ່ວນຫຼຸດນີ້ມີຢູ່ແລ້ວໃນສົກຮຽນນີ້")
    db.refresh(obj)
    return obj


def delete(db: Session, discount_id: str):
    obj = get_by_id(db, discount_id)
    db.delete(obj)
    db.commit()
