from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Province(Base):
    __tablename__ = "province"

    province_id = Column(Integer, primary_key=True, autoincrement=True)
    province_name = Column(String(30), nullable=False)

    districts = relationship("District", back_populates="province")
