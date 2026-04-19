from sqlalchemy import TIMESTAMP, Column, Integer, String, DECIMAL, ForeignKey, func
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Expense(Base):
    __tablename__ = "expense"

    expense_id = Column(Integer, primary_key=True, autoincrement=True)
    expense_category_id = Column(Integer, ForeignKey("expense_category.expense_category_id"), nullable=False)
    salary_payment_id = Column(String(20), ForeignKey("salary_payment.salary_payment_id"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(255), nullable=True)
    expense_date = Column(TIMESTAMP, nullable=False, default=func.now(), server_default=func.now())

    category = relationship("ExpenseCategory", back_populates="expenses")
    salary_payment = relationship("SalaryPayment")
