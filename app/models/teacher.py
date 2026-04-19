from sqlalchemy import Column, Integer, String, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Teacher(Base):
    __tablename__ = "teacher"

    teacher_id = Column(CHAR(5), primary_key=True)
    teacher_name = Column(String(30), nullable=False)
    teacher_lastname = Column(String(30), nullable=False)
    gender = Column(String(10), nullable=False)
    teacher_contact = Column(String(20), nullable=False, unique=True)
    district_id = Column(Integer, ForeignKey("district.district_id"), nullable=False)

    district = relationship("District", back_populates="teachers")
    assignments = relationship("TeacherAssignment", back_populates="teacher")
    salary_payments = relationship("SalaryPayment", back_populates="teacher")
