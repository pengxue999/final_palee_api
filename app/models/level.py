from sqlalchemy import Column, String, CHAR
from sqlalchemy.orm import relationship
from app.configs.database import Base


class Level(Base):
    __tablename__ = "level"

    level_id = Column(CHAR(5), primary_key=True)
    level_name = Column(String(20), nullable=False, unique=True)

    subject_details = relationship("SubjectDetail", back_populates="level")
