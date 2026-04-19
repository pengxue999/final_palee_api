from sqlalchemy import Column, String, DECIMAL, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Discount(Base):
    __tablename__ = "discount"

    discount_id = Column(CHAR(5), primary_key=True)
    academic_id = Column(CHAR(5), ForeignKey("academic_years.academic_id"), nullable=False)
    discount_amount = Column(DECIMAL(10, 2), nullable=False)
    discount_description = Column(String(100), nullable=False)

    academic_year = relationship("AcademicYear", back_populates="discounts")
    registrations = relationship("Registration", back_populates="discount")
