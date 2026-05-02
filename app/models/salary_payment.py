from sqlalchemy import CHAR, Column, DECIMAL, Enum, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.orm import relationship
from app.configs.database import Base


class SalaryPayment(Base):
    __tablename__ = "salary_payment"

    _status_enum = Enum('PAID', 'PARTIAL', name='salary_payment_status')

    salary_payment_id = Column(String(20), primary_key=True)
    teacher_id = Column(
        CHAR(5),
        ForeignKey("teacher.teacher_id", ondelete="RESTRICT"),
        nullable=False,
    )
    user_id = Column(
        Integer,
        ForeignKey("user.user_id", ondelete="RESTRICT"),
        nullable=False,
    )
    month = Column(Integer, nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_date = Column(TIMESTAMP, nullable=False)
    status = Column(_status_enum, nullable=False)

    teacher = relationship("Teacher", back_populates="salary_payments")
    user = relationship("User", back_populates="salary_payments")
