import hashlib

from fastapi import FastAPI, HTTPException, Response, Request, Depends, Form
from typing import Annotated
from sqlalchemy.engine import row
from sqlalchemy.orm import Session
from sqlalchemy import select
from database import get_db
from schemas import (ProductResponse,
                     UserCreate,
                     MessageResponse,
                     UserLogin,
                     HistoryResponse,
                     ProfileEdit)
from models import User,Product,Token, Order, Status
from security import (hash_password,
                      generate_new_token,
                      check_register_data,
                      check_login_data,
                      check_cookies_token)
import python_multipart

from fastapi.responses import JSONResponse


app = FastAPI()


# Эндпоинт, который использует модель Pydantic, для того чтобы собрать корректный ответ
@app.get("/products", response_model=list[ProductResponse])
# Db - переменная которая будет внутри функции. :Session - аннотация, мол ожидается объект типа "Session".
# = Depend(get_db) указывает, что fast api должна сама вызвать функцию, достать результат и активировать блок finally
def get_all_products(db: Session = Depends(get_db)):
    print('START GET ALL PRODUCT ENDPOINT')
    return db.query(Product).all()

# Получить конкретный продукт по id
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product_by_id( product_id: int, db: Session = Depends(get_db)):
     print('START GET SAME PRODUCT ENDPOINT')
     # Запрос в бд
     orm_data = db.query(Product).filter(Product.product_id == product_id).first()
     # Если ничего не найдено, вызвать ошибку
     if orm_data is None:
         raise HTTPException(status_code=404, detail="Product not found")
     # Иначе вернуть ответ
     else:
         return orm_data
@app.get("/users/{user_id}/history", response_model=list[HistoryResponse])
def get_user_history(request: Request, db: Session = Depends(get_db)):
    print('[INFO] START GET USER HISTORY ENDPOINT')
    auth_token = request.cookies.get('auth_token')
    if not auth_token is None:
        print('[INFO] Get token!')
        db_data = db.query(Token).filter(Token.token_value == auth_token).first()
        if db_data is None:
            raise HTTPException(status_code=401, detail="Please log in")
        else:
            stmt = (
                select(Order.order_id,
                       Order.created_at,
                       Order.total_price,
                       Status.status_name
                       )
                .join(Status, Order.status_id == Status.status_id)  # join по status_id
                .where(Order.user_id == db_data.user_id)  # условие отбора по user_id
                .order_by(Order.created_at.desc())  # отсортировать по убыванию
            )
            print(f'[INFO] Sending sql request....: \n\n {stmt}\n')
            result = db.execute(stmt).all()

            # Так называемый list comprehension. Короткая запись перебора result и записи в словарь
            # каждый row представляет собой sql строку с полями, к которым можно обратиться
            history = [
                {
                    'order_id': row.order_id,
                    'created_at': row.created_at,
                    'total_price': row.total_price,
                    'status': row.status_name
                }
                for row in result
            ]

            return history  # Возвращаем ответ
    else:
        raise HTTPException(status_code=401, detail="Please log in")






# Регистрация нового пользователя
@app.post('/register', response_model= MessageResponse)
def register(user: UserCreate, response: Response, db: Session = Depends(get_db)):
    print('\n[INFO] Starting registration process...\n')
    # создание сессии для передачи ее в check_register_data_and_token_generate()
    db = db
    # проверка на уже существующего пользователя с такими данными
    print('\n[INFO] Checking for duplicate...\n')
    check_result, message = check_register_data(user.user_login, user.user_email, db)
    # если такого пользователя нет, производиться создание нового токена в бд, а также нового пользователя
    if check_result:
        print('\n[INFO] Ok!\n')
        # проверка, что пользователь правильно ввел пароль второй раз
        print('\n[INFO] Checking for passwords is match...\n')
        if user.user_password == user.check_password:
            print('\n[INFO] Ok!\n')
            # хеширование пароля
            hashed_password = hash_password(user.user_password)
            # создание orm объекта
            new_user = User(user_login = user.user_login,
                            user_password = hashed_password,
                            user_name = user.user_name,
                            user_email = user.user_email,
                            role_id = 1)
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            # генерация токена
            token = generate_new_token()
            # Добавление токена
            new_token = Token(token_value = token, user_id = new_user.user_id)
            db.add(new_token)
            db.commit()
            db.refresh(new_token)
            print('\n[INFO] Send cookies...\n')
            print('\n[INFO] User have been successfully registered! Sending response...\n')
            # отправка токена в куки
            response.set_cookie(key='auth_token',  # ключ(имя)
                                value=token,  # токен
                                httponly=True,  # чтобы js не имел доступ к кукам (защищает от XSS)
                                samesite= 'lax',  # уровень защиты(отправка куков происходит только при переходе по ссылке)
                                secure= False  # Определяет, по какому протоколу передаются куки(http или https)
            )

                           # См. Файл security
            return message # переменная ответа message содержит в себе словарь с двумя ключами: token_value, message

        else:
            print('\n[INFO] Oops!\n')
            print('\n[INFO] Sending incorrect data response...\n')
            # ответ в случае если пользователь допустил ошибку при повторном вводе пароля
            return {
                'token_value': None,
                'message': 'Passwords do not match'
            }

    else:
        print('\n[INFO] Oops!\n')
        print('\n[INFO] Sending incorrect data response...\n')
        # ответ в случае если пользователь с таким email или login уже существует
        return message


# Аутентификация
@app.post('/login', response_model=MessageResponse)
def login(user: UserLogin, response: Response, request: Request, db: Session = Depends(get_db)):
    print('\n[INFO] Try to get cookies...\n')
    token_from_cookies = request.cookies.get('auth_token')
    db = db

    # если нет токена или токен устарел
    if not token_from_cookies or check_cookies_token(token_from_cookies, db):

        print('\n[INFO] Cookies not found or outdated!\n')
        # проверка данных, которые ввел пользователь и в случае успеха создания по ним токена
        print('\n[INFO] Starting login process...\n')
        print('\n[INFO] Checking login and password...\n')
        result, message, user_id = check_login_data(user.user_login, user.user_password, db)

        # если все ок, созданием ORM объект токен, заносим новый токен в бд и отправляем ответ
        if result:
            print('\n[INFO] Ok!\n')

            token = generate_new_token()
            new_token = Token(token_value = token, user_id = user_id)
            db.add(new_token)
            db.commit()
            db.refresh(new_token)

            print('\n[INFO] Send cookies...\n')
            response.set_cookie(key='auth_token',  # ключ(имя)
                                value=token,  # токен
                                httponly=True,  # чтобы js не имел доступ к кукам
                                samesite='lax',  # уровень защиты(отправка куков происходит только при переходе по ссылке)
                                secure=False  # Определяет, по какому протоколу передаются куки(http или https)
                                )

            print('\n[INFO] User have been successfully login! Sending response...\n')
            return message # You have been login!

        # если что-то не так, отправляется соответствующее сообщение
        else:
            print('\n[INFO] Oops!\n')
            print('\n[INFO] user_password or user_login is incorrect! Sending response...\n')
            return message # Incorrect login or password!
    else:
        print('\n[INFO] Cookies found in db, user already logged in!\n')

        return {
            'message': 'You are already logged in!'
        }

# Выйти из профиля
@app.delete('/logout', response_model=MessageResponse)
def logout(request: Request, response: Response, db: Session = Depends(get_db)):

        # Получаем токен из куков
        token_from_cookies = request.cookies.get('auth_token')
        print('\n[INFO] Get cookies...\n')

        if token_from_cookies:
            # Получаем токен из бд
            token_to_delete = db.query(Token).filter(Token.token_value == token_from_cookies).first()
            print('\n[INFO] Accessing the database for get token...\n')

            # Удаляем строку по токену из бд
            db.delete(token_to_delete)
            db.commit()
            print('\n[INFO] Line with token was successfully deleted!\n')

            # Удаляем куки
            response.delete_cookie(key='auth_token')
            return {
                'message': 'You have been logged out!'
            }
        else:
            return {
                'message': 'You are not logged in!'
            }

@app.patch('/users/{user_id}/edit', response_model=MessageResponse)
def user_profile_edit(  # Принимаем данные из формы. Если данные не пришли, ставим вместо них None
        request: Request,
        user_password: str | None = Form(None),
        user_login: str | None = Form(None),
        user_name: str | None = Form(None),
        user_email: str | None = Form(None),
        db: Session = Depends(get_db),
):
    dict_data = {  # Переписываем данные в словарь
        'user_password': user_password,
        'user_login': user_login,
        'user_name': user_name,
        'user_email': user_email,
    }
    # Переписываем словарь сам в себя, но убираем от туда None
    dict_data = {k:v for k, v in dict_data.items() if v is not None}

    # Получаем токен из куков
    token_from_cookies = request.cookies.get('auth_token')
    print('\n[INFO] Get cookies...\n')

    if token_from_cookies:
        # Получаем user_id по кукам
        user_id = db.query(Token).filter(Token.token_value == token_from_cookies).first().user_id
        if user_id:

            if "user_password" in dict_data:  # Если пользователь передал новый пароль, проводим хеширование
                dict_data["user_password"] = hash_password(dict_data["user_password"])
            # Получаем доступ к экземпляру класса, который нужно поменять(по user_id)
            user_from_db = db.query(User).filter(User.user_id == user_id).first()

            # Перебираем снова словарь и через setattr записываем в нужные нам атрибуты значения ключей
            for key, value in dict_data.items():  # items возвращает пары ключ-знач
                setattr(user_from_db, key, value)  # setattr у конкретного экземпляра меняет заданный атрибут

            db.commit()
            db.refresh(user_from_db)
            print('\n[INFO] User profile data has been updated!\n')
            return {
                'message': 'Your profile data has been updated!'
            }
        else:
            print('\n[INFO] User is not loggen in\n')
            return {
                'message': 'You are not logged in!'
            }
    else:
        print('\n[INFO] User is not loggen in\n')
        return {
            'message': 'You are not logged in!'
        }





