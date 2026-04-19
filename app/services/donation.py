from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from app.models.donor import Donor
from app.models.donation import Donation
from app.models.income import Income
from app.schemas.donation import (
    DonationCreate, DonationUpdate,
)
from app.configs.exceptions import NotFoundException
from app.utils.donation_category import is_cash_donation_name, normalize_donation_category_name


def _build_income_description(donor: Donor | None, donation_name: str) -> str:
    if donor:
        donor_fullname = f"{donor.donor_name} {donor.donor_lastname}".strip()
        if donor_fullname:
            return f"ການບໍລິຈາກ: {donor_fullname}"
    return f"ການບໍລິຈາກ: {donation_name}"


def _get_donor(db: Session, donor_id: str | None) -> Donor | None:
    if not donor_id:
        return None
    return db.query(Donor).filter(Donor.donor_id == donor_id).first()


def _sync_income_record(db: Session, donation: Donation) -> None:
    income = db.query(Income).filter(Income.donation_id == donation.donation_id).first()
    donor = _get_donor(db, donation.donor_id)

    if income:
        income.amount = donation.amount
        income.description = _build_income_description(donor, donation.donation_name)
        income.income_date = donation.donation_date if donation.donation_date else func.now()
    else:
        db.add(
            Income(
                donation_id=donation.donation_id,
                amount=donation.amount,
                description=_build_income_description(donor, donation.donation_name),
                income_date=donation.donation_date if donation.donation_date else func.now(),
            )
        )


def _delete_income_record(db: Session, donation_id: int) -> None:
    income = db.query(Income).filter(Income.donation_id == donation_id).first()
    if income:
        db.delete(income)


def _is_cash_donation_name_for_obj(donation: Donation) -> bool:
    return is_cash_donation_name(donation.donation_category)



def get_all(db: Session):
    return db.query(Donation).options(
        joinedload(Donation.donor),
        joinedload(Donation.unit)
    ).all()


def get_by_id(db: Session, donation_id: int) -> Donation:
    obj = db.query(Donation).options(
        joinedload(Donation.donor),
        joinedload(Donation.unit)
    ).filter(Donation.donation_id == donation_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນການບໍລິຈາກ")
    return obj


def create(db: Session, data: DonationCreate):
    payload = data.model_dump()
    payload["donation_category"] = normalize_donation_category_name(data.donation_category)
    obj = Donation(**payload)
    db.add(obj)
    db.commit()
    db.refresh(obj)

    if is_cash_donation_name(obj.donation_category):
        _sync_income_record(db, obj)
        db.commit()

    return get_by_id(db, obj.donation_id)


def update(db: Session, donation_id: int, data: DonationUpdate):
    obj = get_by_id(db, donation_id)
    old_is_cash = _is_cash_donation_name_for_obj(obj)

    update_data = data.model_dump(exclude_none=True)
    if data.donation_category is not None:
        update_data["donation_category"] = normalize_donation_category_name(
            data.donation_category
        )

    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)

    new_is_cash = _is_cash_donation_name_for_obj(obj)

    if new_is_cash:
        _sync_income_record(db, obj)
        db.commit()

    elif old_is_cash:
        _delete_income_record(db, donation_id)
        db.commit()

    return get_by_id(db, donation_id)


def delete(db: Session, donation_id: int):
    obj = get_by_id(db, donation_id)

    if _is_cash_donation_name_for_obj(obj):
        _delete_income_record(db, donation_id)

    db.delete(obj)
    db.commit()
