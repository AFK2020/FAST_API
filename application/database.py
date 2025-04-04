from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from application.models import Base

# Example: SQLite database URL (you can replace this with PostgreSQL or MySQL)
DATABASE_URL = "sqlite:///./test.db"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create the database tables (you only need to run this once)
def init_db():
    Base.metadata.create_all(bind=engine)