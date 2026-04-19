from sqlalchemy import Column, Integer, String, DateTime, DECIMAL, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class SalaryPayment(Base):
    __tablename__ = "salary_payment"

    salary_payment_id = Column(String(20), primary_key=True)
    teacher_id = Column(CHAR(5), ForeignKey("teacher.teacher_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.user_id"), nullable=False)
    month = Column(Integer, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_date = Column(DateTime, nullable=False)
    status = Column(String(30), nullable=False)

    teacher = relationship("Teacher", back_populates="salary_payments")
    user = relationship("User", back_populates="salary_payments")
