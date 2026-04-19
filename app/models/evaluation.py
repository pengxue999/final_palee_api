from sqlalchemy import Column, String, Date, Enum
from sqlalchemy.orm import relationship
from app.configs.database import Base
from app.enums.semester import SemesterEnum


class Evaluation(Base):
    __tablename__ = "evaluation"

    _semester_enum = Enum(
        SemesterEnum,
        values_callable=lambda items: [item.value for item in items],
    )

    evaluation_id = Column(String(20), primary_key=True)
    semester = Column(_semester_enum, nullable=False)
    evaluation_date = Column(Date, nullable=False)

    evaluation_details = relationship("EvaluationDetail", back_populates="evaluation")
