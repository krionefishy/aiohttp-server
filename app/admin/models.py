from sqlalchemy import Column, Integer, String
from app.store.database.sqlalchemy_base import Base
from dataclasses import dataclass


@dataclass
class Admin:
    id: int
    email: str
    password: str

class AdminModel(Base):
    __tablename__ = "admins"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)