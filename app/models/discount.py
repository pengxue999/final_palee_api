from sqlalchemy import CHAR, Column, DECIMAL, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.discount_description import DiscountDescriptionEnum


class Discount(Base):
    __tablename__ = "discount"

    _description_enum = Enum(
        DiscountDescriptionEnum,
        values_callable=lambda items: [item.value for item in items],
    )

    discount_id = Column(CHAR(5), primary_key=True)
    academic_id = Column(
        CHAR(5),
        ForeignKey("academic_years.academic_id", ondelete="RESTRICT"),
        nullable=False,
    )
    discount_amount = Column(DECIMAL(10, 2), nullable=False)
    discount_description = Column(_description_enum, nullable=False)

    academic_year = relationship("AcademicYear", back_populates="discounts")
    registrations = relationship("Registration", back_populates="discount")
