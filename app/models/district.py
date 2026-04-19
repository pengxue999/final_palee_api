from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class District(Base):
    __tablename__ = "district"

    district_id = Column(Integer, primary_key=True, autoincrement=True)
    district_name = Column(String(30), nullable=False)
    province_id = Column(Integer, ForeignKey("province.province_id"), nullable=False)

    province = relationship("Province", back_populates="districts")
    teachers = relationship("Teacher", back_populates="district")
    students = relationship("Student", back_populates="district")
