from pydantic import BaseModel
from typing import Optional


class AcademicYearInfo(BaseModel):
    academic_id: Optional[str]
    academic_year: str
    status: Optional[str]


class StudentStats(BaseModel):
    total: int
    active: int


class TeacherStats(BaseModel):
    total: int
    active: int


class IncomeStats(BaseModel):
    total: float
    tuition: float
    donation: float
    other: float


class ExpenseStats(BaseModel):
    total: float
    salary: float
    other: float


class DashboardStatsResponse(BaseModel):
    academic_year: AcademicYearInfo
    students: StudentStats
    teachers: TeacherStats
    income: IncomeStats
    expenses: ExpenseStats
    balance: float
