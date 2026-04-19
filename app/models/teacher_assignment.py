from sqlalchemy import Column, String, DECIMAL, CHAR, ForeignKey
from sqlalchemy.orm import relationship
from app.configs.database import Base


class TeacherAssignment(Base):
    __tablename__ = "teacher_assignment"

    assignment_id = Column(CHAR(5), primary_key=True)
    teacher_id = Column(CHAR(5), ForeignKey("teacher.teacher_id"), nullable=False)
    subject_detail_id = Column(CHAR(5), ForeignKey("subject_detail.subject_detail_id"), nullable=False)
    academic_id = Column(CHAR(5), ForeignKey("academic_years.academic_id"), nullable=False)
    hourly_rate = Column(DECIMAL(10, 2), nullable=False)

    teacher = relationship("Teacher", back_populates="assignments")
    subject_detail = relationship("SubjectDetail", back_populates="assignments")
    academic_year = relationship("AcademicYear", back_populates="teacher_assignments")
    teaching_logs = relationship("TeachingLog", foreign_keys="TeachingLog.assignment_id", back_populates="assignment")
