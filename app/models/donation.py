from sqlalchemy import Column, Integer, String, Date, DECIMAL, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Donation(Base):
    __tablename__ = "donation"

    donation_id = Column(Integer, primary_key=True, autoincrement=True)
    donor_id = Column(CHAR(5), ForeignKey("donor.donor_id"), nullable=False)
    donation_category = Column(String(30), nullable=False)
    donation_name = Column(String(30), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    unit_id = Column(Integer, ForeignKey("unit.unit_id"), nullable=False)
    description = Column(String(255), nullable=True)
    donation_date = Column(Date, nullable=False)

    donor = relationship("Donor", back_populates="donations")
    unit = relationship("Unit", back_populates="donations")
