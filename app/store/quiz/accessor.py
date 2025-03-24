from app.base.base_accessor import BaseAccessor
from app.quiz.models import Answer, Question, Theme


class QuizAccessor(BaseAccessor):
    async def create_theme(self, title: str) -> Theme:
        if await self.get_theme_by_title(title):
            raise ValueError("Theme already exists")
        theme = Theme(id=self.app.database.next_theme_id, title=title)
        self.app.database.themes.append(theme)
        return theme

    async def get_theme_by_title(self, title: str) -> Theme | None:
        for t in self.app.database.themes:
            if t.title == title:
                return t
        return None

    async def get_theme_by_id(self, id_: int) -> Theme | None:
        for t in self.app.database.themes:
            if t.id == id_:
                return t
        return None

    async def list_themes(self) -> list[Theme]:
        return self.app.database.themes

    async def get_question_by_title(self, title: str) -> Question | None:
        for q in self.app.database.questions:
            if q.title == title:
                return q
        return None

    async def create_question(
        self, title: str, theme_id: int, answers: list[Answer]
    ) -> Question:
        question = Question(id=self.app.database.next_question_id, title=title, theme_id=theme_id, answers=answers)
        self.app.database.questions.append(question)
        return question

    async def list_questions(self, theme_id: int | None = None) -> list[Question]:
        if theme_id is not None:
            return [
                q for q in self.app.database.questions if q.theme_id == theme_id
            ]
        return self.app.database.questions
