import uuid
from sqlalchemy.orm import Session
import bcrypt
from models import User, Token

# функция для хеширования пароля
def hash_password(user_password: str) -> bytes:
    return bcrypt.hashpw(user_password.encode(), bcrypt.gensalt())


# проверка пароля с хэшем из бд
def check_password(user_password: str, hashed_password: bytes)-> bool:
    valid = bcrypt.checkpw(user_password.encode(), hashed_password)
    return valid
# генерация токена
def generate_new_token():
    return str(uuid.uuid4())


# проверка, нет ли совпадений логина или почты в базе данных
def check_register_data(user_login: str, user_email: str, db):

    response_wrong_l = {
        'message':'User with this login already exists!'
    }

    response_wrong_e = {
        'message': 'User with this email already exists!'
    }

    response_success = {
        'message': 'You have been successfully registered!'
    }

    # запрашиваем пользователя по логину
    login_line = db.query(User).filter(User.user_login == user_login).first()
    # запрашиваем пользователя по почте
    email_line = db.query(User).filter(User.user_email == user_email).first()

    # если найдены строки по логину или паролю, то вернуть ответ в зависимости от совпадения
    if not login_line is None or not email_line is None:
        if not login_line is None:
            return False, response_wrong_l
        else:
            return False, response_wrong_e

    else:
        # ответ в случае если совпадений не найдено
        return True, response_success
# функция для проверки логина и пароля
def check_login_data(user_login: str, user_password: str, db):

    response_invalid_data = {
        'message': 'Incorrect login or password!'
    }
    response_success = {
        'message': 'You have been login!'
    }

    # получения хеша пароля из базы данных(по логину, который принимает на вход функция)
    user = db.query(User).filter(User.user_login == user_login).first()

    if not user:
        return False, response_invalid_data, None

    else:  # иначе, вызываем функцию для сравнения пароля
        password_from_db = user.user_password

        if check_password(user_password, password_from_db):
            user_id = user.user_id
            return True, response_success, user_id
        else:
            return False, response_invalid_data, None

def check_cookies_token(token_from_cookies, db):

    data = db.query(Token).filter(Token.token_value == token_from_cookies).first()

    if data:
       return False

    else:
        return True






