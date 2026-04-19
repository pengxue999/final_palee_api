from sqlalchemy import Column, Integer, String, TIMESTAMP, DECIMAL, ForeignKey, func
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Income(Base):
    __tablename__ = "income"

    income_id = Column(Integer, primary_key=True, autoincrement=True)
    tuition_payment_id = Column(String(20), ForeignKey("tuition_payment.tuition_payment_id"), nullable=True)
    donation_id = Column(Integer, ForeignKey("donation.donation_id"), nullable=True)
    amount = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(255), nullable=True)
    income_date = Column(TIMESTAMP, nullable=False, default=func.now(), server_default=func.now())

    tuition_payment = relationship("TuitionPayment")
    donation = relationship("Donation")
