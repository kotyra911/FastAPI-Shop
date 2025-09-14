from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# ссылка на бд //логин:пароль@адрес:порт/имя_бд
# константа, поэтому большими буквами
SQLALCHEMY_DATABASE_URL: str = 'postgresql+psycopg2://postgres:connectToBase@localhost:5432/Shop'

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
