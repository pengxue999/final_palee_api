from sqlalchemy import CHAR, Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.gender import GenderEnum


class Student(Base):
    __tablename__ = "student"

    _gender_enum = Enum(
        GenderEnum,
        values_callable=lambda items: [item.value for item in items],
    )

    student_id = Column(CHAR(10), primary_key=True)
    student_name = Column(String(30), nullable=False)
    student_lastname = Column(String(30), nullable=False)
    gender = Column(_gender_enum, nullable=False)
    student_contact = Column(String(20), nullable=False)
    parents_contact = Column(String(20), nullable=False)
    school = Column(String(100), nullable=False)
    district_id = Column(
        Integer,
        ForeignKey("district.district_id", ondelete="RESTRICT"),
        nullable=False,
    )

    district = relationship("District", back_populates="students")
    registrations = relationship("Registration", back_populates="student", passive_deletes=True)
