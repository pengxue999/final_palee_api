from sqlalchemy.orm import Session
from app.configs.security import hash_password
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.configs.exceptions import NotFoundException, ConflictException
from sqlalchemy.exc import IntegrityError
from app.utils.foreign_key_helper import safe_delete_with_constraint_check


def get_all(db: Session):
    return db.query(User).all()


def get_by_id(db: Session, user_id: int) -> User:
    obj = db.query(User).filter(User.user_id == user_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນຜູ່ໃຊ້")
    return obj


def create(db: Session, data: UserCreate):
    obj = User(
        user_name=data.user_name,
        user_password=hash_password(data.user_password),
        role=data.role
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def update(db: Session, user_id: int, data: UserUpdate):
    obj = get_by_id(db, user_id)
    update_data = data.model_dump(exclude_none=True)
    if "user_password" in update_data:
        update_data["user_password"] = hash_password(update_data["user_password"])
    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, user_id: int):
    obj = get_by_id(db, user_id)
    safe_delete_with_constraint_check(db, obj, "user")
