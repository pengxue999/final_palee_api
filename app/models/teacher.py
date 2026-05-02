from sqlalchemy import CHAR, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.gender import GenderEnum


class Teacher(Base):
    __tablename__ = "teacher"

    _gender_enum = Enum(
        GenderEnum,
        values_callable=lambda items: [item.value for item in items],
    )

    teacher_id = Column(CHAR(5), primary_key=True)
    teacher_name = Column(String(30), nullable=False)
    teacher_lastname = Column(String(30), nullable=False)
    gender = Column(_gender_enum, nullable=False)
    teacher_contact = Column(String(20), nullable=False, unique=True)
    district_id = Column(
        Integer,
        ForeignKey("district.district_id", ondelete="RESTRICT"),
        nullable=False,
    )

    district = relationship("District", back_populates="teachers")
    assignments = relationship("TeacherAssignment", back_populates="teacher")
    salary_payments = relationship("SalaryPayment", back_populates="teacher")
