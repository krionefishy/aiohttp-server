from app.quiz.schemes import ThemeSchema, QuestionSchema, QuestionListResponseSchema
from app.web.app import View
from app.web.utils import json_response, auth_required
from aiohttp_apispec import request_schema, response_schema, docs
from app.web.schemes import OkResponseSchema
from aiohttp.web_exceptions import HTTPConflict, HTTPBadRequest, HTTPNotFound
import json
class ThemeAddView(View):
    @docs(
        tags=["quiz"],
        summary="Add theme",
        description="Add new quiz theme",
        responses={
            200: {"description": "Theme added successfully"},
            400: {"description": "Invalid data"},
            401: {"description": "Unauthorized"},
            409: {"description": "Theme already exists"}
        }
    )
    @response_schema(OkResponseSchema, 200)
    async def post(self):
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



class ThemeListView(View):
    @docs(
        tags=["admin"],
        summary="current admin",
        description="Получение текущего админа",
        responses={
            200: {"description": "успешно получили тему"},
            401: {"description": "нет cookie"},
            403: {"description": "невалидные данные"},
            409: {"description": "тема уже существует"}
        }
    )
    @response_schema(OkResponseSchema, 200)
    async def get(self):
        themes = await self.request.app.store.quizzes.list_themes()
        data = []
        for i in themes:
            data.append({"id": i.id, "title": i.title})
        resp = json_response(
            data= { 
                "themes": data,
            }
        )
        return resp


class QuestionAddView(View):
    @docs(
        tags=["admin"],
        summary="current admin",
        responses={
            200: {"description": "успешно получили тему"},
            401: {"description": "нет cookie"},
            403: {"description": "невалидные данные"},
            409: {"description": "тема уже существует"}
        }
    ) 
    @response_schema(OkResponseSchema, 200)
    async def post(self):
            data = await self.request.json()
            
            required_fields = ['title', 'theme_id', 'answers']
            missing = [field for field in required_fields if field not in data]
            if missing:
                raise HTTPBadRequest(
                    text=json.dumps({
                        "status": "bad_request",
                        "json": f"Missing required fields: {', '.join(missing)}",
                        "data": {"missing_fields": missing}
                    }),
                    content_type="application/json"
                )
            
            title = data['title'].strip()
            theme_id = data['theme_id']
            answers = data['answers']
            
            if not isinstance(answers, list) or len(answers) < 2:
                raise HTTPBadRequest(
                    text=json.dumps({
                        "status": "bad_request",
                        "json": "Unprocessable Entity",
                        "data": {}
                    }),
                    content_type="application/json"
                )
            
            correct_answers = sum(1 for a in answers if a.get('is_correct', False))
            if correct_answers == 0:
                raise HTTPBadRequest(
                    text=json.dumps({
                        "status": "bad_request",
                        "message": "At least one correct answer required",
                        "data": {}
                    }),
                    content_type="application/json"
                )
            if correct_answers > 1:
                raise HTTPBadRequest(
                    text=json.dumps({
                        "status": "bad_request",
                        "message": "Only one correct answer allowed",
                        "data": {}
                    }),
                    content_type="application/json"
                )
            
            if not await self.store.quizzes.get_theme_by_id(theme_id):
                raise HTTPNotFound(
                    text=json.dumps({
                        "status": "not_found",
                        "message": "Theme not found",
                        "data": {}
                    }),
                    content_type="application/json"
                )
            
            if await self.store.quizzes.get_question_by_title(title):
                raise HTTPConflict(
                    text=json.dumps({
                        "status": "conflict",
                        "message": "Question already exists",
                        "data": {}
                    }),
                    content_type="application/json"
                )
            
            question = await self.store.quizzes.create_question(
                title=title,
                theme_id=theme_id,
                answers=answers
            )
            
            return json_response(data={
                "id": question.id,
                "title": question.title,
                "theme_id": question.theme_id,
                "answers": question.answers
            })
            

class QuestionListView(View):
    @docs(tags=["quiz"])
    @response_schema(QuestionListResponseSchema, 200)
    async def get(self):
        theme_id = self.request.query.get("theme_id")
        
        if theme_id:
            try:
                theme_id = int(theme_id)
                if not await self.store.quizzes.get_theme_by_id(theme_id):
                    raise HTTPNotFound(reason=f"Theme {theme_id} not found")
            except ValueError:
                raise HTTPBadRequest(reason="Invalid theme_id format")

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