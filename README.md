# Проект: Интернет-Магазин техники
Backend для интернет-магазина на FastAPI + PostgreSQL

## Технологии
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic
- Pytest

## Установка
1. Клонируем репозиторий:
   ```bash
   git clone https://github.com/kotyra911/FastAPI-Shop.git)
   cd FastAPI-Shop
   
2. Создаем виртуальное окржуение и активируем(ниже пример для Windows):
   ```bash
   python -m venv venv
   venv\Scripts\activate

3. Установка зависимостей:
   ```bash
   pip install requirements.txt

4. Создайте файл .env на основе .env_example

5. Запуск сервера:
   ```bash
   uvicorn handler:app
   или
   uvicorn handler:app --reload (сервер будет самостоятельно перезагружаться при изменениях)

## Навигация 


### .py
1. tests/ --> Тесты (pytest)
2. handler.py --> Содержит сам app а также все эндпоинты
3. database.py --> Содержит движок, фабрику сессий и функцию по созданию новой сессии
4. models.py --> ORM модели базы данных
5. schemas.py --> Pydantic-схемы
6. security --> Разнообразные функции для проверки данных, хеширование и т.п.
### tools
1. SqlScripts/ --> Содержит важные SQL запросы(например скрипт создания бд)
2. pytest.ini --> Конфиг файл для настройки pytest
3. requirements.txt --> Файл с зависимостями
4. .env_example --> Содержит пример содержимого для .env, который вы сами создаете

## Пример запроса через командную строку(curl)

      ```bash
      curl -X GET "http://127.0.0.1:8000/products" -H "accept: application/json"


## Связаться со мной



   
