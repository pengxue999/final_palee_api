from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.expense_category import ExpenseCategory
from app.schemas.expense_category import ExpenseCategoryCreate, ExpenseCategoryUpdate
from app.configs.exceptions import NotFoundException, ConflictException


def get_all(db: Session):
    return db.query(ExpenseCategory).all()


def get_by_id(db: Session, category_id: int) -> ExpenseCategory:
    obj = db.query(ExpenseCategory).filter(ExpenseCategory.expense_category_id == category_id).first()
    if not obj:
        raise NotFoundException("ຂໍ້ມູນປະເພດລາຍຈ່າຍ")
    return obj


def create(db: Session, data: ExpenseCategoryCreate):
    obj = ExpenseCategory(**data.model_dump())
    db.add(obj)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ປະເພດລາຍຈ່າຍ '{data.expense_category}' ມີຢູ່ແລ້ວ")


def update(db: Session, category_id: int, data: ExpenseCategoryUpdate):
    obj = get_by_id(db, category_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    try:
        db.commit()
        db.refresh(obj)
        return obj
    except IntegrityError:
        db.rollback()
        raise ConflictException(f"ປະເພດລາຍຈ່າຍ '{data.expense_category}' ມີຢູ່ແລ້ວ")


def delete(db: Session, category_id: int):
    obj = get_by_id(db, category_id)
    db.delete(obj)
    db.commit()
