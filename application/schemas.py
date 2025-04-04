from datetime import date
from pydantic import BaseModel, EmailStr, field_validator

from sqlalchemy.ext.declarative import declarative_base

from enum import Enum


Base = declarative_base()


class Department(Enum):
    HR = "HR"
    SALES = "SALES"
    IT = "IT"
    ENGINEERING = "ENGINEERING"


class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr
    date_of_birth: date
    role: str
    department: Department
    salary: float
    elected_benefits: bool

    @field_validator("date_of_birth")
    @classmethod
    def check_valid_age(cls, date_of_birth: date) -> date:
        today = date.today()
        eighteen_years_ago = date(today.year - 18, today.month, today.day)

        if date_of_birth > eighteen_years_ago:
            raise ValueError("Employees must be at least 18 years old.")
        return date_of_birth


""""
class Employee(BaseModel):
    employee_id: UUID = Field(default_factory=uuid4, frozen=True)
    name: str = Field(min_length=1, frozen=True)
    email: EmailStr  #EmailStr is validator for email 
    date_of_birth: date = Field(alias="birth_date", repr=False, frozen=True) # repr: if this should be displayed in model field representation
    role : str = Field(max_length=50)
    department : Department
    salary: float = Field(alias="compensation", gt=0, repr=False)
    elected_benefits : bool


    @field_validator("date_of_birth")
    @classmethod
    def check_valid_age(cls, date_of_birth: date) -> date:
        today = date.today()
        eighteen_years_ago = date(today.year - 18, today.month, today.day)

        if date_of_birth > eighteen_years_ago:
            raise ValueError("Employees must be at least 18 years old.")
        return date_of_birth
    
    @model_validator(mode="after")    # mode=after => Pydantic waits until after you’ve instantiated your model to run the method
    def check_it_benefits(self) -> Self:
        department = self.department
        elected_benefits = self.elected_benefits

        if department == Department.IT and elected_benefits:
            raise ValueError(
                "IT employees are contractors and don't qualify for benefits"
            )
        return self
        """
