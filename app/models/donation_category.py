from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from app.configs.database import Base


class DonationCategory(Base):
    __tablename__ = "donation_category"

    donation_category_id = Column(Integer, primary_key=True, autoincrement=True)
    donation_category_name = Column(String(30), nullable=False, unique=True)

    donations = relationship("Donation", back_populates="donation_category")