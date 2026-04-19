from sqlalchemy import Column, String, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Subject(Base):
    __tablename__ = "subject"

    subject_id = Column(CHAR(5), primary_key=True)
    subject_name = Column(String(20), nullable=False, unique=True)
    subject_category_id = Column(CHAR(5), ForeignKey("subject_category.subject_category_id"), nullable=False)

    category = relationship("SubjectCategory", back_populates="subjects")
    subject_details = relationship("SubjectDetail", back_populates="subject")
