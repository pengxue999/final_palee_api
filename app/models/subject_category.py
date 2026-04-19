from sqlalchemy import Column, String, CHAR
from sqlalchemy.orm import relationship
from app.configs.database import Base


class SubjectCategory(Base):
    __tablename__ = "subject_category"

    subject_category_id = Column(CHAR(5), primary_key=True)
    subject_category_name = Column(String(20), nullable=False, unique=True)

    subjects = relationship("Subject", back_populates="category")
