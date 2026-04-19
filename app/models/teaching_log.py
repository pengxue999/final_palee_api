from sqlalchemy import Column, Integer, String, ForeignKey, Text, CHAR, DECIMAL, Enum as SAEnum, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.configs.database import Base


class TeachingLog(Base):
    __tablename__ = "teaching_log"

    teaching_log_id = Column(Integer, primary_key=True, autoincrement=True)
    assignment_id = Column(CHAR(5), ForeignKey("teacher_assignment.assignment_id"), nullable=False)
    substitute_for_assignment_id = Column(CHAR(5), ForeignKey("teacher_assignment.assignment_id"), nullable=True, default=None)
    teaching_date = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    hourly = Column(DECIMAL(5, 2), nullable=False)
    remark = Column(String(255), default=None)
    status = Column(SAEnum('ຂຶ້ນສອນ', 'ຂາດສອນ', name='teaching_log_status'), nullable=True, default='ຂຶ້ນສອນ')

    assignment = relationship("TeacherAssignment", foreign_keys=[assignment_id], back_populates="teaching_logs")
    substitute_assignment = relationship("TeacherAssignment", foreign_keys=[substitute_for_assignment_id])
