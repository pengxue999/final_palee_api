from sqlalchemy.orm import Session, joinedload
from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate
from app.configs.exceptions import NotFoundException


def get_all(db: Session):
    return db.query(Expense).options(joinedload(Expense.category)).all()


def get_by_id(db: Session, expense_id: int) -> Expense:
    obj = db.query(Expense).options(joinedload(Expense.category)).filter(Expense.expense_id == expense_id).first()
    if not obj:
        raise NotFoundException("ຂໍູ້ມູນລາຍຈ່າຍ")
    return obj


def create(db: Session, data: ExpenseCreate):
    obj = Expense(**data.model_dump())
    db.add(obj)
    db.commit()
    return get_by_id(db, obj.expense_id)


def update(db: Session, expense_id: int, data: ExpenseUpdate):
    obj = get_by_id(db, expense_id)
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, expense_id: int):
    obj = get_by_id(db, expense_id)
    db.delete(obj)
    db.commit()
