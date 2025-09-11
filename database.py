from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Database URL //login:password@url:port/database_name
# upper because this is const
SQLALCHEMY_DATABASE_URL: str = 'postgresql+psycopg2://postgres:connectToBase@localhost:5432/Shop'

# engine create. Contain connection with database
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#Basic models class
Base = declarative_base()

#Session fabric for connections and sending requests in database
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# return new session
def get_db():

    try:
        db = SessionLocal()

        yield db

    finally:
        db.close()

