from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL, Enum, CHAR
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.scholarship import ScholarshipEnum


class RegistrationDetail(Base):
    __tablename__ = "registration_detail"

    regis_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    registration_id = Column(String(20), ForeignKey("registration.registration_id", ondelete="CASCADE"), nullable=False)
    fee_id = Column(CHAR(5), ForeignKey("fee.fee_id"), nullable=False)
    scholarship = Column(Enum(ScholarshipEnum, values_callable=lambda x: [e.value for e in x]), nullable=False)

    registration = relationship("Registration", back_populates="details")
    fee_rel = relationship("Fee", back_populates="registration_details")
    evaluation_details = relationship("EvaluationDetail", back_populates="registration_detail", passive_deletes=True)
