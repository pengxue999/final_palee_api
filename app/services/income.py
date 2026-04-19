from sqlalchemy.orm import Session, joinedload
from app.models.income import Income
from app.models.donation import Donation
from app.schemas.income import IncomeCreate, IncomeUpdate
from app.configs.exceptions import NotFoundException, ValidationException
from app.utils.donation_category import is_cash_donation_name


def _query(db: Session):
    return db.query(Income).options(
        joinedload(Income.tuition_payment),
        joinedload(Income.donation),
    )


def _validate_donation_income_link(db: Session, donation_id: int | None) -> None:
    if donation_id is None:
        return

    donation = db.query(Donation).filter(Donation.donation_id == donation_id).first()
    if not donation:
        raise NotFoundException("ຂໍ້ມູນການບໍລິຈາກ")

    if not is_cash_donation_name(donation.donation_category):
        raise ValidationException("ສາມາດບັນທຶກລາຍຮັບຈາກການບໍລິຈາກໄດ້ສະເພາະປະເພດເງິນສົດ")


def get_all(db: Session):
    return _query(db).all()


def get_by_id(db: Session, income_id: int) -> Income:
    obj = _query(db).filter(Income.income_id == income_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນລາຍຮັບ")
    return obj


def create(db: Session, data: IncomeCreate):
    _validate_donation_income_link(db, data.donation_id)
    obj = Income(**data.model_dump())
    db.add(obj)
    db.commit()
    return get_by_id(db, obj.income_id)


def update(db: Session, income_id: int, data: IncomeUpdate):
    obj = get_by_id(db, income_id)
    _validate_donation_income_link(db, data.donation_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, income_id: int):
    obj = get_by_id(db, income_id)
    db.delete(obj)
    db.commit()
