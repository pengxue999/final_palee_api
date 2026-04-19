from sqlalchemy import Column, String, CHAR
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Donor(Base):
    __tablename__ = "donor"

    donor_id = Column(CHAR(5), primary_key=True)
    donor_name = Column(String(30), nullable=False)
    donor_lastname = Column(String(30), nullable=False)
    donor_contact = Column(String(20), nullable=False, unique=True)
    section = Column(String(255), nullable=True)

    donations = relationship("Donation", back_populates="donor")
