from sqlalchemy import Column, DECIMAL, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Fee(Base):
    __tablename__ = "fee"

    fee_id = Column(CHAR(5), primary_key=True)
    subject_detail_id = Column(CHAR(5), ForeignKey("subject_detail.subject_detail_id"), nullable=False)
    academic_id = Column(CHAR(5), ForeignKey("academic_years.academic_id"), nullable=False)
    fee = Column(DECIMAL(10, 2), nullable=False)

    subject_detail = relationship("SubjectDetail", back_populates="fees")
    academic_year = relationship("AcademicYear", back_populates="fees")
    registration_details = relationship("RegistrationDetail", back_populates="fee_rel")
