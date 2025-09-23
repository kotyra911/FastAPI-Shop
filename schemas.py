from datetime import datetime
from fastapi import Form
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

class UserLogin(BaseModel):
    user_login: str
    user_password: str

class MessageResponse(BaseModel):  # Схема для отправки сообщения
    message: str

class HistoryResponse(BaseModel):  # Схема для отправки истории
    order_id: int
    created_at: datetime
    total_price: float
    status: str

class CartItemsToAdd(BaseModel):  # Схема для получения объектов на добавление в корзину
    product_id: int
    quantity: int

    class Config:
        orm_mode = True

class CartItems(BaseModel):  # Схема для отправки содержимого корзины
    product_name: str
    quantity: int
    total_price: float

    class Config:
        orm_mode = True

class AddProduct(BaseModel):
    product_name: str
    product_price: float
    units_in_stock: int

class DeleteProduct(BaseModel):
    product_id: int


