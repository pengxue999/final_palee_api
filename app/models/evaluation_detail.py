from sqlalchemy import CHAR, Column, DECIMAL, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.configs.database import Base


class EvaluationDetail(Base):
    __tablename__ = "evaluation_detail"

    eval_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(
        CHAR(10),
        ForeignKey("evaluation.evaluation_id", ondelete="RESTRICT"),
        nullable=False,
    )
    regis_detail_id = Column(
        Integer,
        ForeignKey("registration_detail.regis_detail_id", ondelete="RESTRICT"),
        nullable=False,
    )
    score = Column(DECIMAL(5, 2), nullable=False)
    ranking = Column(CHAR(10), nullable=False)
    prize = Column(DECIMAL(10, 2), nullable=True)

    evaluation = relationship("Evaluation", back_populates="evaluation_details")
    registration_detail = relationship("RegistrationDetail", back_populates="evaluation_details")
