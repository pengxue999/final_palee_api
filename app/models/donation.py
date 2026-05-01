from sqlalchemy import Column, Integer, String, Date, DECIMAL, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Donation(Base):
    __tablename__ = "donation"

    donation_id = Column(Integer, primary_key=True, autoincrement=True)
    donor_id = Column(CHAR(5), ForeignKey("donor.donor_id"), nullable=False)
    donation_category_id = Column(
        Integer,
        ForeignKey("donation_category.donation_category_id"),
        nullable=False,
    )
    donation_name = Column(String(30), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    unit = Column(String(30), nullable=False)
    donation_date = Column(Date, nullable=False)

    donor = relationship("Donor", back_populates="donations")
    donation_category = relationship("DonationCategory", back_populates="donations")
