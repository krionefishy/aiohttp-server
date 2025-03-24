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
    @request_schema(ThemeSchema)
    async def post(self):
        try:
            title = self.data["title"]
            
            # Проверка существования темы
            if await self.store.quizzes.get_theme_by_title(title):
                raise HTTPConflict(
                    text=json.dumps({
                        "status": "conflict",
                        "message": "Theme already exists",
                        "data": {}
                    }),
                    content_type="application/json"
                )
            
            # Создание темы
            theme = await self.store.quizzes.create_theme(title=title)
            
            return json_response(data={
                "id": theme.id,
                "title": theme.title
            })

        except json.JSONDecodeError:
            raise HTTPBadRequest(
                text=json.dumps({
                    "status": "bad_request",
                    "message": "Invalid JSON",
                    "data": {}
                }),
                content_type="application/json"
            )


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
        description="Получение текущего админа",
        responses={
            200: {"description": "успешно получили тему"},
            401: {"description": "нет cookie"},
            403: {"description": "невалидные данные"},
            409: {"description": "тема уже существует"}
        }
    )
    
    @request_schema(QuestionSchema)
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        title = self.request["data"]["title"]
        theme_id = self.request["data"]["theme_id"]
        answers = self.request["data"]["answers"]
        if len(answers) <= 1:
            raise HTTPBadRequest(reason="only one answer")
        

        count_of_correct = 0
        for ans in answers:
            if ans["is_correct"] == True:
                count_of_correct += 1
            if count_of_correct > 1:
                raise HTTPBadRequest(reason="too many correct answers")
        
        if count_of_correct == 0:
            raise HTTPBadRequest(reason="zero correct answers")
        
        theme_exists = await self.request.app.store.quizzes.get_theme_by_id(theme_id)
        if not theme_exists:
            raise HTTPNotFound(reason="theme not found")
            
        existing_question = await self.request.app.store.quizzes.get_question_by_title(title)
        if existing_question:
            raise HTTPConflict(reason="question with such title already exists")

        question = await self.request.app.store.quizzes.create_question(title,theme_id, answers)
        return json_response(
            data={
                "id": question.id,
                "title": question.title,
                "theme_id": theme_id,
                "answers": question.answers
            }
        )


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