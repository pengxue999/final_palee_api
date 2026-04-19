from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.configs.database import Base


class ExpenseCategory(Base):
    __tablename__ = "expense_category"

    expense_category_id = Column(Integer, primary_key=True, autoincrement=True)
    expense_category = Column(String(30), nullable=False)

    expenses = relationship("Expense", back_populates="category")
