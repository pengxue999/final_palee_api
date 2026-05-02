from sqlalchemy import CHAR, Column, Date
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.academic_status import AcademicStatusEnumSQL


class AcademicYear(Base):
    __tablename__ = "academic_years"

    academic_id = Column(CHAR(5), primary_key=True)
    academic_year = Column(CHAR(10), nullable=False, unique=True)
    start_date_at = Column(Date, nullable=False)
    end_date_at = Column(Date, nullable=False)
    status = Column(AcademicStatusEnumSQL, nullable=False)

    fees = relationship("Fee", back_populates="academic_year")
    discounts = relationship("Discount", back_populates="academic_year")
    teacher_assignments = relationship("TeacherAssignment", back_populates="academic_year")
