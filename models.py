# models.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from sqlalchemy.orm import DeclarativeBase, mapped_column, relationship
from sqlalchemy import Integer, String, Float, ForeignKey

db = SQLAlchemy()

class Base(DeclarativeBase):
    pass

class User(db.Model, UserMixin):
    id = mapped_column(Integer, primary_key=True)
    email = mapped_column(String(150), unique=True, nullable=False)
    name = mapped_column(String(150), nullable=False)
    password = mapped_column(String(150), nullable=False)
    balance = mapped_column(Float, nullable=False, default=0.0)
    items = relationship('Item', back_populates='owner')


class Item(db.Model):
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(length=30), nullable=False, unique=True)
    price = mapped_column(Float, nullable=False)
    barcode = mapped_column(String(length=12), nullable=False, unique=True)
    description = mapped_column(String(length=1024), nullable=False)
    owner_id = mapped_column(Integer, ForeignKey('user.id'))
    owner = relationship('User', back_populates='items')

    def __repr__(self):
        return f"<Item {self.id}: {self.name}>"
