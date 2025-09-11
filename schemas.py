from pydantic import BaseModel


class ProductResponse(BaseModel):  # to process the response(SQLAlchemy) data
    product_id: int
    product_name: str
    product_price: float
    units_in_stock: int

    class Config:
        orm_mode = True

class UserCreate(BaseModel):  # to process the request data
    user_login: str
    user_password: str
    user_email: str
    user_name: str
    check_password: str

class AuthResponse(BaseModel):  # to process the response(SQLAlchemy) data
    token_value: str
    message: str

class RegistrationResponse(BaseModel):  # to process the response(SQLAlchemy) data
    token_value: str | None
    message: str
