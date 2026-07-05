from sqlalchemy.orm import Session
from app.models.registration_detail import RegistrationDetail
from app.models.fee import Fee
from app.schemas.registration_detail import RegistrationDetailCreate, RegistrationDetailUpdate
from app.configs.exceptions import NotFoundException, ConflictException, ValidationException
from app.utils.foreign_key_helper import safe_delete_with_constraint_check
from app.services import registration as registration_svc


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


def _ensure_not_locked(db: Session, registration_id: str):
    """ຈ່າຍແລ້ວ → ບໍ່ໃຫ້ແກ້ໄຂ/ລຶບວິຊາເກົ່າ."""
    if registration_svc.is_registration_locked(db, registration_id):
        raise ConflictException(
            "ການລົງທະບຽນນີ້ຈ່າຍເງິນແລ້ວ ບໍ່ສາມາດແກ້ໄຂ ຫຼື ລຶບວິຊາໄດ້"
        )


def update(db: Session, regis_detail_id: int, data: RegistrationDetailUpdate):
    obj = get_by_id(db, regis_detail_id)
    _ensure_not_locked(db, obj.registration_id)

    update_data = data.model_dump(exclude_none=True)
    # ບໍ່ໃຫ້ຍ້າຍວິຊາໄປ registration ອື່ນ
    update_data.pop("registration_id", None)

    # ຖ້າປ່ຽນວິຊາ (fee_id) ຕ້ອງຢູ່ສົກຮຽນດຽວກັນ ແລະ ບໍ່ຊໍ້າກັບວິຊາທີ່ມີຢູ່ແລ້ວ
    new_fee_id = update_data.get("fee_id")
    if new_fee_id is not None and new_fee_id != obj.fee_id:
        new_fee = db.query(Fee).filter(Fee.fee_id == new_fee_id).first()
        if new_fee is None:
            raise ValidationException("ບໍ່ພົບຂໍ້ມູນວິຊາ")

        old_fee = db.query(Fee).filter(Fee.fee_id == obj.fee_id).first()
        if old_fee is not None and new_fee.academic_id != old_fee.academic_id:
            raise ValidationException("ບໍ່ສາມາດປ່ຽນໄປວິຊາຈາກສົກຮຽນອື່ນໄດ້")

        duplicate = db.query(RegistrationDetail).filter(
            RegistrationDetail.registration_id == obj.registration_id,
            RegistrationDetail.fee_id == new_fee_id,
            RegistrationDetail.regis_detail_id != regis_detail_id,
        ).first()
        if duplicate is not None:
            raise ConflictException("ວິຊານີ້ໄດ້ລົງທະບຽນແລ້ວ")

    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)

    # ຄຳນວນຈຳນວນເງິນ/ສ່ວນຫຼຸດ/ສະຖານະຄືນ
    registration_svc.recompute_registration(db, obj.registration_id)
    return obj


def delete(db: Session, regis_detail_id: int):
    obj = get_by_id(db, regis_detail_id)
    _ensure_not_locked(db, obj.registration_id)
    registration_id = obj.registration_id

    safe_delete_with_constraint_check(db, obj, "registration_detail")

    # ຄຳນວນຄືນ (ຈະລຶບການລົງທະບຽນ ຖ້າບໍ່ເຫຼືອວິຊາ)
    registration_svc.recompute_registration(db, registration_id)
