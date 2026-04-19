from sqlalchemy import Column, String, Date, Enum
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.academic_status import AcademicStatusEnumSQL


class AcademicYear(Base):
    __tablename__ = "academic_years"

    academic_id = Column(String(5), primary_key=True)
    academic_year = Column(String(10), nullable=False, unique=True)
    start_date_at = Column(Date, nullable=True)
    end_date_at = Column(Date, nullable=True)
    status = Column(AcademicStatusEnumSQL, nullable=False)

    fees = relationship("Fee", back_populates="academic_year")
    discounts = relationship("Discount", back_populates="academic_year")
    teacher_assignments = relationship("TeacherAssignment", back_populates="academic_year")
