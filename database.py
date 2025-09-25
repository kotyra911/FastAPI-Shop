from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

db_password = os.getenv("DB_PASSWORD")
db_user = os.getenv("DB_USER")
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_port = os.getenv("DB_PORT")
SQLALCHEMY_DATABASE_URL: str = f'postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# создание движка, содержит соединение с бд
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#Базовый класс модели
Base = declarative_base()

#Создание фабрики сессий, через которые будут отправляться запросы
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# функция для создания новой сессии
def get_db():

    try:
        db = SessionLocal()

        yield db

    finally:
        db.close()
