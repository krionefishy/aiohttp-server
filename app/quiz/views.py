from aiohttp.web import json_response
from aiohttp_apispec import docs, response_schema
from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from sqlalchemy.orm import selectinload
import json

from app.quiz.schemes import (
    QuestionListResponseSchema,
    ThemeListResponseSchema
)
from app.web.app import View
from app.web.utils import json_response
from app.web.schemes import OkResponseSchema
from app.quiz.models import AnswerModel

class ThemeAddView(View):
    @docs(
        tags=["quiz"],
        summary="Add theme",
        description="Add new quiz theme",
    )
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        try:
            data = await self.request.json()
            
            if not isinstance(data, dict) or 'title' not in data or not isinstance(data['title'], str) or not data['title'].strip():
                raise HTTPBadRequest(
                    reason="Unprocessable Entity",
                    text=json.dumps({
                        "json": {"title": ["Missing data for required field."]}
                    })
                )

            title = data['title']
            

            theme = await self.request.app.store.quizzes.create_theme(title=title)
            return json_response(data={"id": theme.id, "title": theme.title})
            
        except IntegrityError:
            raise HTTPConflict(
                reason="Theme already exists",
                text=json.dumps({
                    "status": "conflict",
                    "message": "Theme already exists",
                    "data": {}
                })
            )
        except json.JSONDecodeError:
            raise HTTPBadRequest(
                reason="Invalid JSON",
                text=json.dumps({
                    "status": "bad_request",
                    "message": "Invalid JSON data",
                    "data": {}
                })
            )


class ThemeListView(View):
    @docs(
        tags=["quiz"],
        summary="List themes",
        description="Get all quiz themes",
    )
    @response_schema(ThemeListResponseSchema, 200)
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(data={
            "themes": [{"id": t.id, "title": t.title} for t in themes]
        })


class QuestionAddView(View):
    @docs(
        tags=["quiz"],
        summary="Add question",
        description="Add new quiz question",
    )
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        try:
            data = await self.request.json()
            
            
            required_fields = ['title', 'theme_id', 'answers']
            if missing := [field for field in required_fields if field not in data]:
                raise HTTPBadRequest(
                    text=json.dumps({
                        "status": "bad_request",
                        "message": f"Missing required fields: {', '.join(missing)}",
                        "data": {"missing_fields": missing}
                    }),
                    content_type="application/json"
                )
            
            title = data['title'].strip()
            theme_id = data['theme_id']
            answers = data['answers']
            
            store = self.request.app.store
            try:
                await store.quizzes.get_theme_by_id(theme_id) 
            except HTTPNotFound:
                raise HTTPNotFound(reason=f"Theme with id {theme_id} not found")
            if not isinstance(answers, list) or len(answers) < 2:
                raise HTTPBadRequest(
                    text=json.dumps({
                        "status": "bad_request",
                        "message": "At least two answers required",
                        "data": {}
                    }),
                    content_type="application/json"
                )
            
            correct_answers = sum(1 for a in answers if a.get('is_correct', False))
            if correct_answers != 1:
                raise HTTPBadRequest(
                    text=json.dumps({
                        "status": "bad_request",
                        "message": "Exactly one correct answer required",
                        "data": {}
                    }),
                    content_type="application/json"
                )
            

            answer_models = [
                AnswerModel(title=a["title"], is_correct=a["is_correct"])
                for a in answers
            ]
            
            question = await self.store.quizzes.create_question(
                title=data['title'].strip(),
                theme_id=data['theme_id'],
                answers=answer_models
            )
        
            
            return json_response(data={
                "id": question.id,
                "title": question.title,
                "theme_id": question.theme_id,
                "answers": [
                    {"title": a.title, "is_correct": a.is_correct}
                    for a in question.answers  
                ]
            })
            
        
        except json.JSONDecodeError:
            raise HTTPBadRequest(
                text=json.dumps({
                    "status": "bad_request",
                    "message": "Invalid JSON data",
                    "data": {}
                }),
                content_type="application/json"
            )
        

class QuestionListView(View):
    @docs(
        tags=["quiz"],
        summary="List questions",
        description="Get quiz questions",
    )
    @response_schema(QuestionListResponseSchema, 200)
    async def get(self):
        theme_id = self.request.query.get("theme_id")
        
        if theme_id:
            try:
                theme_id = int(theme_id)
                if not await self.store.quizzes.get_theme_by_id(theme_id):
                    raise HTTPNotFound(
                        reason="Theme not found",
                        text=json.dumps({
                            "status": "not_found",
                            "message": f"Theme {theme_id} not found",
                            "data": {}
                        })
                    )
            except ValueError:
                raise HTTPBadRequest(
                    reason="Invalid theme_id",
                    text=json.dumps({
                        "status": "bad_request",
                        "message": "theme_id must be integer",
                        "data": {}
                    })
                )

        questions = await self.store.quizzes.list_questions(
            theme_id=theme_id if theme_id else None
        )

        return json_response(data={
            "questions": [{
                "id": q.id,
                "title": q.title,
                "theme_id": q.theme_id,
                "answers": [
                    {"title": a.title, "is_correct": a.is_correct}
                    for a in q.answers
                ]
            } for q in questions]
        })