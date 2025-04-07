import os
from typing import Optional
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum
from fastapi import FastAPI, HTTPException, Depends, status
from sqlalchemy.orm import Session, relationship, validates
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing_extensions import Self
from datetime import date
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator
from passlib.context import CryptContext

from fastapi.security import OAuth2PasswordBearer

from sqlalchemy import (
    Boolean,
    Column,
    String,
    Integer,
    Float,
    Date,
    # Enum as SqlAlchemyEnum,
)
from sqlalchemy.ext.declarative import declarative_base

from uuid import UUID, uuid4
from enum import Enum
from fastapi.security import OAuth2PasswordRequestForm


import jwt
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # take environment variables

# OAuth2PasswordBearer automatically looks for the 'Authorization' header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 60 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ['JWT_SECRET_KEY']   # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ['JWT_REFRESH_SECRET_KEY']    # should be kept secret


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    """Generate a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=REFRESH_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_REFRESH_SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})
        return email  # Returning the user's email or a user object from the DB
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"})


app = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class Department(Enum):
    HR = "HR"
    SALES = "SALES"
    IT = "IT"
    ENGINEERING = "ENGINEERING"


# Ensure to print the path of the database to check where it is located
# print(f"Database file path: {os.path.abspath('mydatabase.db')}")

# Define the Base and Engine (use a file-based SQLite database)
engine = create_engine(
    "sqlite:///mydatabase.db", echo=True
)  # Ensure this points to a file, not memory
Base = declarative_base()


# Define the Employee model
class Employee(Base):
    __tablename__ = "employees"

    employee_id= Column(String, primary_key=True, default=lambda: str(uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    date_of_birth = Column(Date, nullable=False)
    role = Column(String, nullable=False)
    department = Column(SQLAlchemyEnum(Department), nullable=False)
    salary = Column(Float, nullable=False)
    elected_benefits = Column(Boolean, nullable=False)

    def __repr__(self):
        return f"<Employee(employee_id={self.employee_id}, name={self.name})>"




class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    def __repr__(self):
        return f"<User(username={self.username}, email={self.email})>"



    def set_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
    
    def check_password(self, password: str):
        return pwd_context.verify(password, self.hashed_password)

Base.metadata.create_all(engine)

db_session = sessionmaker(bind=engine)
session = db_session()

employee1 = Employee(
    name="Clyde Harwell",
    email="charwell@example.com",
    date_of_birth=datetime.strptime("2000-06-12", "%Y-%m-%d").date(),
    salary=100_000,
    department="ENGINEERING",
    elected_benefits=True,
    role="dev",
)

employee2 = Employee(
    name="AK",
    email="ak@example.com",
    date_of_birth=datetime.strptime("1999-10-02", "%Y-%m-%d").date(),
    salary=100_000,
    department="ENGINEERING",
    elected_benefits=True,
    role="dev",
)

# # Insert into the database
# session.add_all([employee1, employee2])
# session.commit()

"""
# Query and print records
employees = session.query(Employee).all()
for employee in employees:
    print(employee)

"""

employee = session.query(Employee).filter_by(name ="AK").first()
print(employee)

users = session.query(User).all()
for user in users:
    print(user)



class EmployeeCreate(BaseModel):
    name: str
    email: EmailStr  # Email validation
    date_of_birth: date
    role: str
    department: Department
    salary: float
    elected_benefits: bool

    class Config:
        orm_mode = True  # This tells Pydantic to work with SQLAlchemy ORM models

    @field_validator("date_of_birth")
    @classmethod
    def check_valid_age(cls, date_of_birth: date) -> date:
        today = date.today()
        eighteen_years_ago = date(today.year - 18, today.month, today.day)

        if date_of_birth > eighteen_years_ago:
            raise ValueError("Employees must be at least 18 years old.")
        return date_of_birth


# Create a new employee
def create_employee_in_db(db: Session, employee: EmployeeCreate):
    db_employee = Employee(
        name=employee.name,
        email=employee.email,
        date_of_birth=employee.date_of_birth,
        role=employee.role,
        department=employee.department,
        salary=employee.salary,
        elected_benefits=employee.elected_benefits,
    )
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


class EmployeeUpdate(BaseModel):        # Pydantic Schema. For validations
    name: Optional[str]
    email: Optional[EmailStr]  # Email validation
    role: Optional[str]
    salary: Optional[float]

    class Config:
        orm_mode = True  # This tells Pydantic to work with SQLAlchemy ORM models

def update_employee_in_db( employee_id:str , db: Session, employee= EmployeeUpdate):
    print("In Method", employee_id)

    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    print(db_employee)
    print(employee.name)
    if not db_employee:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    if employee.name:
        print(db_employee.name)
        db_employee.name = employee.name
        print(db_employee.name)

    if employee.email:
        db_employee.email = employee.email
    if employee.role:
        db_employee.role= employee.role
    if employee.salary:
        db_employee.salary = employee.salary
    
    # Check if the session is dirty (if any changes were made)
    if db_employee in db.dirty:
        print(f"Employee {db_employee.employee_id} is dirty, committing changes.")
        db.commit()
    else:
        print("No changes detected. Skipping commit.")

    db.refresh(db_employee)
    
    return db_employee




# Dependency to get the database session
def get_db():
    db = session
    try:
        yield db
    finally:
        db.close()


@app.post("/employees/")
async def create_employee(employee: EmployeeCreate, db: Session = Depends(get_db), current_user: str = Depends(get_current_user)):
    db_employee = create_employee_in_db(db=db, employee=employee)
    return db_employee


@app.patch("/employee/{employee_id}")
async def update_employee(employee_id: str ,employee:EmployeeUpdate, db: Session = Depends(get_db),  current_user: str = Depends(get_current_user)):
    print(employee_id)
    updated_employee = update_employee_in_db(employee_id=employee_id, db=db , employee=employee )
    return updated_employee

@app.get("/employee/{employee_id}")
async def get_employee(employee_id: str, db: Session = Depends(get_db),  current_user: str = Depends(get_current_user)):
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()
    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
     
    return db_employee

@app.delete("/employee/{employee_id}")
async def get_employee(employee_id: str, db: Session = Depends(get_db),  current_user: str = Depends(get_current_user)):
    db_employee = db.query(Employee).filter(Employee.employee_id == employee_id).first()

    if db_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    db.delete(db_employee)
    db.commit()

    return db_employee



class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        orm_mode = True


def create_user(user: UserCreate, db: Session):
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    db_user_by_username = db.query(User).filter(User.username == user.username).first()
    if db_user_by_username:
        raise HTTPException(status_code=400, detail="Username already taken")

    # Create a new user and hash the password
    new_user = User(username=user.username, email=user.email)
    new_user.set_password(user.password)
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
    


@app.post("/register/")
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    new_user = create_user(user=user, db=db)
    return new_user



class UserLogin(BaseModel):
    email: EmailStr
    password: str



@app.post("/login/")
async def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user or not db_user.check_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # A claim is a piece of information about the user or system that is encoded into the JWT. Claims can be used to represent things like the user's ID, email, roles, permissions    
    access_token = create_access_token(data={"sub": db_user.email}) # sub is short for subject. It's one of the standard claims in JWT.
    refresh_token = create_refresh_token(data={"sub": db_user.email})
    return {"access_token": access_token, "refresh_token" : refresh_token,"token_type": "bearer"}


"""
@app.get("/")
async def root():
    return {"message": "Hello World"}
"""