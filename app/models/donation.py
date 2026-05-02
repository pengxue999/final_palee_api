from sqlalchemy import CHAR, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Donation(Base):
    __tablename__ = "donation"

    donation_id = Column(Integer, primary_key=True, autoincrement=True)
    donor_id = Column(
        CHAR(5),
        ForeignKey("donor.donor_id", ondelete="RESTRICT"),
        nullable=False,
    )
    donation_category_id = Column(
        Integer,
        ForeignKey("donation_category.donation_category_id", ondelete="RESTRICT"),
        nullable=False,
    )
    donation_name = Column(String(30), nullable=False)
    amount = Column(Float, nullable=False)
    unit = Column(String(10), nullable=False)
    donation_date = Column(Date, nullable=False)

    donor = relationship("Donor", back_populates="donations")
    donation_category = relationship("DonationCategory", back_populates="donations")
