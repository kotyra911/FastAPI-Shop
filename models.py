from sqlalchemy import Column, String, Integer, Numeric, DateTime, LargeBinary, TIMESTAMP, func
from database import Base
from sqlalchemy import ForeignKey


# Create table model by SQLAlchemy
class Product(Base):
    __tablename__ = 'products'
    #Создание колонок, все то же самое, что и в SQL, только описывается другими словами
    product_id = Column(Integer, primary_key=True, index=True)
    product_name = Column(String(30), nullable=False)
    product_price = Column(Numeric(10,2), nullable=False)
    units_in_stock = Column(Integer, nullable=False)

class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True, index=True)
    user_login = Column(String(30),unique=True, nullable=False)
    user_password = Column(LargeBinary, nullable=False)
    user_name = Column(String(30), nullable=False)
    user_email = Column(String(40), unique=True, nullable=False)
    role_id = Column(Integer, ForeignKey('roles.role_id'))

class Token(Base):
    __tablename__ = 'tokens'
    token_id = Column(Integer, primary_key=True, index=True)
    token_value = Column(String(255), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'))

class Role(Base):
    __tablename__ = 'roles'
    role_id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(20),unique=True, nullable=False)

class Order(Base):
    __tablename__ = 'orders'
    order_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now()) # Время будет выставляться в бд, а не в питоне
    total_price = Column(Numeric(10,2), nullable=False)
    status_id = Column(Integer, ForeignKey('statuses.status_id'))

class Status(Base):
    __tablename__ = 'statuses'
    status_id = Column(Integer, primary_key=True, index=True)
    status_name = Column(String(20), nullable=False)

class CartItem(Base):
    __tablename__ = 'cartitems'
    cart_item_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.user_id'))
    product_id = Column(Integer, ForeignKey('products.product_id'))
    quantity = Column(Integer, nullable=False)
    total_price = Column(Numeric(10,2), nullable=False)








