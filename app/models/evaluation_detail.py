from sqlalchemy import Column, Integer, String, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from app.configs.database import Base


class EvaluationDetail(Base):
    __tablename__ = "evaluation_detail"

    eval_detail_id = Column(Integer, primary_key=True, autoincrement=True)
    evaluation_id = Column(String(20), ForeignKey("evaluation.evaluation_id"), nullable=False)
    regis_detail_id = Column(Integer, ForeignKey("registration_detail.regis_detail_id", ondelete="CASCADE"), nullable=False)
    score = Column(DECIMAL(5, 2), nullable=False)
    ranking = Column(Integer, nullable=False, default=0)
    prize = Column(DECIMAL(10, 2), nullable=True)

    evaluation = relationship("Evaluation", back_populates="evaluation_details")
    registration_detail = relationship("RegistrationDetail", back_populates="evaluation_details")
