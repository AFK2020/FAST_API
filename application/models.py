from typing_extensions import Self
from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from sqlalchemy import Column, String, Integer, Float, Date, Enum as SqlAlchemyEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from uuid import UUID, uuid4
from enum import Enum


Base = declarative_base()


class Department(Enum):
    HR = "HR"
    SALES = "SALES"
    IT = "IT"
    ENGINEERING = "ENGINEERING"


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    date_of_birth = Column(Date, nullable=False)
    role = Column(String, nullable=False)
    department = Column(SqlAlchemyEnum(Department), nullable=False)
    salary = Column(Float, nullable=False)
    elected_benefits = Column(bool, nullable=False)

    def __repr__(self):
        return f"<Employee(employee_id={self.employee_id}, name={self.name})>"
