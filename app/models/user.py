from sqlalchemy import Column, Enum, Integer, String
from sqlalchemy.orm import relationship
from app.configs.database import Base


class User(Base):
    __tablename__ = "user"

    _role_enum = Enum('DIRECTOR', 'TEACHER', name='user_role')

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(30), nullable=False, unique=True)
    user_password = Column(String(255), nullable=False)
    role = Column(_role_enum, nullable=False)

    salary_payments = relationship("SalaryPayment", back_populates="user")
