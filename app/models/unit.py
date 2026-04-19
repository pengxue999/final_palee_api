from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Unit(Base):
    __tablename__ = "unit"

    unit_id = Column(Integer, primary_key=True, autoincrement=True)
    unit_name = Column(String(30), nullable=False, unique=True)

    donations = relationship("Donation", back_populates="unit")
