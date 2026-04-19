from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.configs.database import Base


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    user_name = Column(String(30), nullable=False)
    user_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)

    salary_payments = relationship("SalaryPayment", back_populates="user")
