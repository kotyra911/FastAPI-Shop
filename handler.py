
from fastapi import FastAPI, HTTPException
from fastapi import Depends
from sqlalchemy.orm import Session
from database import get_db
from schemas import ProductResponse, UserCreate, AuthResponse, RegistrationResponse
from models import User,Product,Token
from security import hash_password, generate_new_token, check_login_and_reg_data

from fastapi.responses import JSONResponse


app = FastAPI()


@app.get("/ping")
def ping():
    return {"message": "pong"}

# Эндпоинт, который использует модель Pydantic, для того чтобы собрать корректный ответ
@app.get("/products", response_model=list[ProductResponse])
# db - переменная которая будет внутри функции. :Session - аннотация, мол ожидается объект типа "Session".
# = Depend(get_db) указывает, что fast api должна сама вызвать функцию, достать результат и активировать блок finally
def get_all_products(db: Session = Depends(get_db)):
    return db.query(Product).all()

# Получить конкретный продукт по id
@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product_by_id( product_id: int, db: Session = Depends(get_db)):
     # Запрос в бд
     orm_data = db.query(Product).filter(Product.product_id == product_id).first()
     # Если ничего не найдено, вызвать ошибку
     if orm_data is None:
         raise HTTPException(status_code=404, detail="Product not found")
     # Иначе вернуть ответ
     else:
         return orm_data


# Registration new user

@app.post('/register', response_model= RegistrationResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    #hashing password
    user_password = hash_password(user.user_password)
    if user.user_password == user.check_password:
        db = db
        status, message =check_login_and_reg_data(user.user_login, user.user_email, None, db)
        if status:

            # Create new instance of class User, by data from Pydantic model
            new_user = User(user_login = user.user_login,user_password = user_password,
                            user_name = user.user_name,user_email = user.user_email, role_id = 1)
            db.add(new_user)
            db.commit()  # commit for save in database
            db.refresh(new_user)  # refresh to take actual datas

            token = generate_new_token()  # generate token

            # Create new instance of class Token, by data from generate and Pydantic
            new_token = Token(token_value = token, user_id = new_user.user_id)
            db.add(new_token)
            db.commit()
            db.refresh(new_token)

            print(f'New user {new_user.user_login} was successfully registered!')
            message = 'You have successfully registered!'

            return {
                'token_value': token,
                'message': message
                    }
        else:
            return {
                'token_value': None,
                'message': message  # User with this log/email already exist!
            }
    else:
        message = "Passwords do not match!"
        return {
            'message': message
        }



