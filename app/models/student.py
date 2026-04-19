from sqlalchemy import Column, Integer, String, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Student(Base):
    __tablename__ = "student"

    student_id = Column(CHAR(10), primary_key=True)
    student_name = Column(String(30), nullable=False)
    student_lastname = Column(String(30), nullable=False)
    gender = Column(String(10), nullable=False)
    student_contact = Column(String(20), nullable=False)
    parents_contact = Column(String(20), nullable=False)
    school = Column(String(100), nullable=False)
    district_id = Column(Integer, ForeignKey("district.district_id"), nullable=False)

    district = relationship("District", back_populates="students")
    registrations = relationship("Registration", back_populates="student", passive_deletes=True)
