from sqlalchemy import Column, Integer, String, Date, DECIMAL, CHAR, ForeignKey, Enum, TIMESTAMP
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.registration_status import RegistrationStatusEnum


class Registration(Base):
    __tablename__ = "registration"

    registration_id = Column(String(20), primary_key=True)
    student_id = Column(CHAR(10), ForeignKey("student.student_id", ondelete="CASCADE"), nullable=False)
    discount_id = Column(CHAR(5), ForeignKey("discount.discount_id", ondelete="SET NULL"), nullable=True)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    final_amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(RegistrationStatusEnum, values_callable=lambda e: [x.value for x in e]), nullable=False)
    registration_date = Column(TIMESTAMP, nullable=False)

    student = relationship("Student", back_populates="registrations")
    discount = relationship("Discount", back_populates="registrations")
    details = relationship("RegistrationDetail", back_populates="registration", passive_deletes=True)
    tuition_payments = relationship("TuitionPayment", back_populates="registration", passive_deletes=True)
