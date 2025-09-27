import pytest
from pygments.lexers import q

from database import Base
from database import engine
from fastapi.testclient import TestClient
from handler import app
from sqlalchemy.orm import Session
from models import Product, User, Role, Status, Token, CartItem
from database import SessionLocal

client = TestClient(app)

#Подготовка тестовой базы
@pytest.fixture(scope="session", autouse=True)
def setup_db(db_session: Session):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    new_role1 = Role(role_name="user")
    db_session.add(new_role1)
    new_role2 = Role(role_name="admin")
    db_session.add(new_role2)

    new_status = Status(status_name="Оформляется")
    new_status1 = Status(status_name="Оплачен")
    new_status2 = Status(status_name="Отправлен")

    new_product = Product(product_name="Iphone 15", product_price=1500, units_in_stock=10)
    new_product1 = Product(product_name="MacBook Pro", product_price=1500, units_in_stock=10)

    db_session.add_all([new_product, new_product1, new_status, new_status1, new_status2])
    db_session.commit()


# Подготовка сессии
@pytest.fixture(scope="session", autouse=True)
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Проверка эндпоинта получения списка всех продуктов
def test_det_all_products(db_session: Session):
    response = client.get("/products")
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Проверяем, что пришел именно список строк

# Проверка эндпоинта регистрации нового пользователя
def test_register(db_session: Session):
    # Первичная регистрация
    data_to_send = {"user_login": "NewUser",
                    "user_password": "12345",
                    "user_name": "Andrey",
                    "user_email": "email@example.com",
                    "check_password": "12345"}

    response = client.post("/register", json=data_to_send)  # Отправляет запрос со словарем в формате JSON
    assert response.status_code == 200  # Ожидаем ответ 200
    # Достаем пользователя, которого только что добавили
    user_from_db = db_session.query(User).filter(User.user_login == data_to_send.get("user_login")).first()
    assert user_from_db is not None  # Проверяем, что данные действительно пришли из бд
    assert user_from_db.user_login == data_to_send.get("user_login")  # Проверяем, что они совпадают с отправленными

    # Запрос регистрации по таким же данным
    data_to_send = {"user_login": "NewUser",
                    "user_password": "12345",
                    "user_name": "Andrey",
                    "user_email": "email@example.com",
                    "check_password": "12345"}
    response = client.post("/register", json=data_to_send)
    assert response.status_code == 200
    assert response.json() == {"message": "User with this login already exists!"}  # В ответ ожидаем сообщение

    #Запрос без данных регистрации
    response = client.post("/register")
    assert response.status_code == 422  # Ожидаем 422 статус код и словарь с ругательствами от FastAPI

    # Проверка ответа на не совпадающие пароли
    data_to_send = {"user_login": "Other",
                    "user_password": "12345",
                    "user_name": "Andrey",
                    "user_email": "email2@example.com",
                    "check_password": "1234"}
    response = client.post("/register", json=data_to_send)
    assert response.status_code == 200
    assert response.json() == {"message": "Passwords do not match"}  # В ответ ожидаем сообщение

# Проверка эндпоинта аутентификации пользователя
def test_login(db_session: Session):

    data_to_login = {
        "user_login": "NewUser",
        "user_password": "12345"
    }
    user_id = db_session.query(User).filter(User.user_login == data_to_login.get("user_login")).first().user_id
    token_from_db = db_session.query(Token).filter(Token.user_id == user_id).first()
    db_session.delete(token_from_db)

    response = client.post("/login", json=data_to_login)
    cookies = response.cookies # Достаем куки и проверяем, что они есть
    assert response.status_code == 200
    print('cookies')
    assert cookies is not None
    print('success')
    token_from_db = db_session.query(Token).filter(Token.user_id == user_id).first()
    assert token_from_db is not None  # Проверяем что токен есть действительно

    response = client.post("/login", json=data_to_login)
    assert response.status_code == 200
    assert response.json() == {"message": "You are already logged in!"}  # В ответ ожидаем сообщение
    # Удаляем токен из базы, чтобы сервер понял, что не прошли аутентификацию
    db_session.delete(token_from_db)
    db_session.commit()
    # Данные, которых нет в бд
    data_to_incorrect_login = {
        "user_login": "blablabla",
        "user_password": "1756456"
    }
    response = client.post("/login", json=data_to_incorrect_login)
    assert response.status_code == 200
    assert response.json() == {"message": "Incorrect login or password!"}


def test_select_same_product():
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.json()["product_id"] == 1
    assert isinstance(response.json()["product_price"], float)

def test_cart_add_product(db_session: Session):
    data_to_send = {
        "product_id": 1,
        "quantity": 1
    }
    # Проверяем случай, если не прошедший аутентификацию пользователь, пытается открыть корзину
    response = client.post("/products/1/add",json=data_to_send)
    assert response.status_code == 401
    assert response.json() == {"detail": "Please login first!"}

    data_to_login = {
        "user_login": "NewUser",
        "user_password": "12345"
    }

    data_to_send = {
                    "product_id": 1,
                    "quantity": 1
                   }
    response = client.post("/login", json=data_to_login)  # Логинимся

    response = client.post("/products/1/add",json=data_to_send)  # Отправляем нормальный запрос
    # Проверяем, что ответ пришел нормальный
    assert response.status_code == 200
    assert response.json() == {'message': 'Added to your cart!'}
    # Проверяем, что в базу занеслись правильные данные
    user_id = db_session.query(User).filter(User.user_login == data_to_login.get("user_login")).first().user_id
    cart_data = db_session.query(CartItem).filter(CartItem.user_id == user_id).first()
    assert cart_data.quantity == data_to_send.get("quantity")

    # Пробуем добавить товар, которого нет на складе
    product_from_db = db_session.query(Product).filter(Product.product_id == data_to_send.get("product_id")).first()
    product_from_db.units_in_stock = 0
    db_session.commit()
    response = client.post("/products/1/add",json=data_to_send)
    assert response.status_code == 200
    assert response.json() == {'message': 'The product is out of stock :('}

    # Запрос на товар, который не существует
    data_to_send = {
        "product_id": 27,
        "quantity": 1
    }
    response = client.post("/products/1/add",json=data_to_send)
    assert response.status_code == 200
    assert response.json() == {"message": "This product does not exist!"}

    # Отправка запроса без каких либо данных
    response = client.post("/products/1/add")
    assert response.status_code == 422  # Ответ содержит ругательства, что не заполнены нужные поля


def test_get_same_cart():

    # Получаем корзину будучи аутентифицированным пользователем
    response = client.get("users/1/cart")
    assert response.status_code == 200
    assert response.json()["items"][0].get("product_name") == "Iphone 15"
    assert response.json()["total_price"] == 1500

    # Пытаемся получить корзину без аутентификации
    client.cookies.clear()
    response = client.get("users/1/cart")
    assert response.status_code == 401
    assert response.json() == {"detail": "Please login first!"}

