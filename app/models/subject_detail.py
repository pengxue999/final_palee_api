from sqlalchemy import Column, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class SubjectDetail(Base):
    __tablename__ = "subject_detail"

    subject_detail_id = Column(CHAR(5), primary_key=True)
    subject_id = Column(CHAR(5), ForeignKey("subject.subject_id"), nullable=False)
    level_id = Column(CHAR(5), ForeignKey("level.level_id"), nullable=False)

    subject = relationship("Subject", back_populates="subject_details")
    level = relationship("Level", back_populates="subject_details")
    fees = relationship("Fee", back_populates="subject_detail")
    assignments = relationship("TeacherAssignment", back_populates="subject_detail")
