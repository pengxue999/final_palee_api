from sqlalchemy import CHAR, Column, DECIMAL, Enum as SAEnum, ForeignKey, Integer, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.configs.database import Base


class TeachingLog(Base):
    __tablename__ = "teaching_log"

    _status_enum = SAEnum('TEACHING', 'ABSENT', name='teaching_log_status')

    teaching_log_id = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id = Column(
        CHAR(5),
        ForeignKey("teacher_assignment.assignment_id", ondelete="RESTRICT"),
        nullable=False,
    )
    substitute_for_assignment_id = Column(
        CHAR(5),
        ForeignKey("teacher_assignment.assignment_id", ondelete="SET NULL"),
        nullable=True,
        default=None,
    )
    teaching_date = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    hourly = Column(DECIMAL(5, 2), nullable=False)
    status = Column(_status_enum, nullable=False, default='TEACHING')

    assignment = relationship("TeacherAssignment", foreign_keys=[assignment_id], back_populates="teaching_logs")
    substitute_assignment = relationship("TeacherAssignment", foreign_keys=[substitute_for_assignment_id])
