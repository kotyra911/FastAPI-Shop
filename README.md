# Проект: Интернет-Магазин техники
Backend для интернет-магазина на FastAPI + PostgreSQL

## Технологии
- Python 3.11
- FastAPI
- SQLAlchemy
- PostgreSQL
- Pydantic

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
   uvicorn handler:app --reload (сервер будет самостоятельно перезагружаться при изминениях)

   
