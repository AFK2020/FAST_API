from sqlalchemy.orm import Session
from .models import Employee
from .schemas import EmployeeCreate

# Create a new employee
def create_employee(db: Session, employee: EmployeeCreate):
    db_employee = Employee(
        name=employee.name,
        email=employee.email,
        date_of_birth=employee.date_of_birth,
        role=employee.role,
        department=employee.department,
        salary=employee.salary,
        elected_benefits=employee.elected_benefits
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee