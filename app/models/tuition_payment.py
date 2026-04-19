from sqlalchemy import Column, Enum, String, Date, DECIMAL, ForeignKey, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.payment_method import PaymentMethodEnum


class TuitionPayment(Base):
    __tablename__ = "tuition_payment"

    tuition_payment_id = Column(String(20), primary_key=True)
    registration_id = Column(String(20), ForeignKey("registration.registration_id", ondelete="CASCADE"), nullable=False)
    paid_amount = Column(DECIMAL(10, 2), nullable=False)
    payment_method = Column(
        Enum(PaymentMethodEnum, values_callable=lambda e: [x.value for x in e]),
        nullable=False,
    )
    pay_date = Column(TIMESTAMP, nullable=False, default=func.now(), server_default=func.now())

    registration = relationship("Registration", back_populates="tuition_payments")
