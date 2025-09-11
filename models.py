from sqlalchemy import Column, String, Integer, Numeric, DateTime, LargeBinary
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
