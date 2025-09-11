import uuid
from sqlalchemy.orm import Session
import bcrypt
from models import User

# hash-function
def hash_password(user_password: str) -> bytes:
    user_password = bcrypt.hashpw(user_password.encode(), bcrypt.gensalt())
    return user_password

# check of password correct
def check_password(hashed_password: bytes, password: str)-> bool:

    return bcrypt.checkpw(password.encode(), hashed_password)


# token generating
def generate_new_token():
    return str(uuid.uuid4())

def check_login_and_reg_data(
                             user_login:str,
                             user_email:str = None,
                             user_password:str = None,
                             db: Session = None
                             ):
    try:
        # it's mean the function need make registration data check
        if user_password is None:

            check_login_line = db.query(User).filter(User.user_login == user_login).first()
            check_email_line = db.query(User).filter(User.user_email == user_email).first()

            if not check_login_line is None or not check_email_line is None:
                if not check_login_line is None:

                    return False, 'User with this login already exists'
                else:

                    return False, 'User with this email already exists'

            else:
                return True, None
        # it's mean the function need make login data check
        else:
            password_from_db = (db.query(User).filter(User.user_login == user_login).first()).user_password

            valid = check_password(password_from_db, user_password)

            if valid:
                return True
            else:
                return False
    except Exception as e:
        print(f'Ошибка {e}')








