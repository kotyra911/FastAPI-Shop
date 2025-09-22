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

class MessageResponse(BaseModel):
    message: str

class HistoryResponse(BaseModel):
    order_id: int
    created_at: datetime
    total_price: float
    status: str

class ProfileEdit(BaseModel):
        user_password: bytes | None = None
        user_login: str | None = None
        user_name: str | None = None
        user_email: str | None = None



