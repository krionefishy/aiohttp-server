from app.web.app import View
from app.admin.models import Admin
from app.web.utils import error_json_response, json_response
from app.store.admin.accessor import AdminAccessor
from app.admin.schemes import AdminSchema
from aiohttp_apispec import docs, response_schema, request_schema
from app.web.schemes import OkResponseSchema
from app.store.admin.accessor import AdminAccessor
import bcrypt
import uuid
from app.web.utils import auth_required
from datetime import datetime, timedelta


class AdminLoginView(View):
    @docs(tags=["admin"],
            description="adm auth",
            responses={
            200: {"description": "Успешная авторизация"},
            403: {"description": "Неправильный пароль/почта"},
            400: {"description": "Переданы не все параметры"}
        })
    @response_schema(OkResponseSchema, 200)
    @request_schema(AdminSchema)
    async def post(self):

        data = self.request["data"]
        
        current = await self.request.app.store.admins.get_by_email(data["email"])
        if current is None:
            return error_json_response(
                http_status=403,
                status="forbidden",
                message="admin not found, but we dont use 404 bcs we are 🤡",
            )

        if not bcrypt.checkpw(data["password"].encode("utf-8"), current.password.encode("utf-8")):
            return error_json_response(
                http_status=403,
                status = "forbidden",
                message="hohoho wrong password/email",
            )
        
        session_id = str(uuid.uuid4())
        await self.request.app["CookieStorage"].create_session(current.id, session_id)

        resp= json_response(

            data = {
                "id": current.id,
                "email": current.email}
        )
        resp.set_cookie(
            name="session_id", 
            value=session_id,
            expires=datetime.now() + timedelta(days=1)
        )
        
        return resp


class AdminCurrentView(View):
    @docs(
        tags=["admin"],
        summary="current admin",
        description="Получение текущего админа",
        responses={
            200: {"description": "успешно получили админа"},
            401: {"description": "нет cookie"},
            403: {"description": "невалидные cookie"}
        }
    )
    @response_schema(OkResponseSchema, 200)
    @auth_required
    async def get(self):
        admin = {
            "id": self.request.admin.id,
            "email": self.request.admin.email
        }

        resp = json_response(
            data=admin
        )

        return resp
