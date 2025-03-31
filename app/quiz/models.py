from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.store.database.sqlalchemy_base import Base

from dataclasses import dataclass
from typing import List


@dataclass
class Theme:
    id: int | None  
    title: str

@dataclass
class Question:
    id: int
    theme_id: int
    title: str
    answers: List["Answer"]


@dataclass
class Answer:
    title: str
    is_correct: bool

class ThemeModel(Base):
    __tablename__ = "themes"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)
    
    questions = relationship("QuestionModel", back_populates="theme", cascade="all, delete-orphan")

    def __init__(self, title: str):
        self.title = title



class QuestionModel(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, unique=True, nullable=False)
    theme_id = Column(Integer, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    
    theme = relationship("ThemeModel", back_populates="questions")
    answers = relationship("AnswerModel", back_populates="question", cascade="all, delete-orphan")


    def __init__(self, title: str, theme_id: int, answers: List[Answer] = None):
        self.title = title
        self.theme_id = theme_id
        if answers:
            self.answers = answers


class AnswerModel(Base):
    __tablename__ = "answers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False, nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    
    question = relationship("QuestionModel", back_populates="answers")