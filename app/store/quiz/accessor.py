from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from aiohttp.web_exceptions import  HTTPNotFound

from app.base.base_accessor import BaseAccessor
from app.quiz.models import *
from app.quiz.models import Answer, Question, Theme


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> ThemeModel:
        async with self.app.database.session() as session:
            try:
                theme_model = ThemeModel(title=title)
                session.add(theme_model)
                await session.commit()
                await session.refresh(theme_model)
                return theme_model
            except IntegrityError:
                await session.rollback()
                raise  
    async def get_theme_by_title(self, title: str) -> Theme | None:
        async with self.app.database.session() as session:
            theme_model = await session.scalar(
                select(ThemeModel).where(ThemeModel.title == title)
            )
            if theme_model:
                return theme_model 
            return None

    async def get_theme_by_id(self, id_: int) -> Theme:
        async with self.app.database.session() as session:
            theme_model = await session.scalar(
                select(ThemeModel).where(ThemeModel.id == id_)
            )
            if not theme_model:
                raise HTTPNotFound(reason=f"Theme with id {id_} not found")
            return theme_model

    async def list_themes(self) -> list[Theme]:
        async with self.app.database.session() as session:
            themes_model = await session.scalars(select(ThemeModel))
            return [
                Theme(id=theme.id, title=theme.title)
                for theme in themes_model
            ]

    async def get_question_by_title(self, title: str) -> Question | None:
        async with self.app.database.session() as session:
            question = await session.scalar(
                select(QuestionModel)
                .where(QuestionModel.title == title)
                .options(selectinload(QuestionModel.answers))
            )
            if not question:
                return None
            
            return Question(
                id=question.id,
                title=question.title,
                theme_id=question.theme_id,
                answers=[
                    Answer(title=answer.title, is_correct=answer.is_correct)
                    for answer in question.answers
                ]
            )

    async def create_question(self, title: str, theme_id: int, answers: list[AnswerModel] = []) -> QuestionModel:
        async with self.app.database.session() as session:
            try:
                question_model = QuestionModel(title=title, theme_id=theme_id)
                session.add(question_model)
                await session.flush()

                answer_models = []
                for answer in answers:
                    answer_model = AnswerModel(
                        title=answer.title,
                        is_correct=answer.is_correct,
                        question_id=question_model.id,
                    )
                    session.add(answer_model)
                    answer_models.append({
                        "title": answer_model.title,
                        "is_correct": answer_model.is_correct
                    })
                
                await session.commit()
                
                await session.refresh(question_model)
                full_question = await session.execute(
                    select(QuestionModel)
                    .where(QuestionModel.id == question_model.id)
                    .options(selectinload(QuestionModel.answers)))
                return full_question.scalar_one()
                
            except IntegrityError:
                await session.rollback()
                raise

    async def list_questions(self, theme_id: int | None = None) -> list[Question]:
        async with self.app.database.session() as session:
            query = select(QuestionModel).options(
                selectinload(QuestionModel.answers)
            )
            
            if theme_id is not None:
                query = query.where(QuestionModel.theme_id == theme_id)
            
            questions = await session.scalars(query)
            
            return [
                Question(
                    id=question.id,
                    title=question.title,
                    theme_id=question.theme_id,
                    answers=[
                        Answer(title=answer.title, is_correct=answer.is_correct)
                        for answer in question.answers
                    ]
                )
                for question in questions
            ]