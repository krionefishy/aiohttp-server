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
from app.web.utils import auth_required, validate_request
from datetime import datetime, timedelta
import json
from aiohttp.web_exceptions import HTTPBadRequest


class AdminLoginView(View):
    @response_schema(OkResponseSchema, 200)
    async def post(self):
        try:
            data = await self.request.json()
            
            # Проверка обязательных полей
            if 'email' not in data or 'password' not in data:
                missing = []
                if 'email' not in data: missing.append('email')
                if 'password' not in data: missing.append('password')
                raise HTTPBadRequest(
                    text=json.dumps({
                        "status": "bad_request",
                        "message": f"Missing required fields: {', '.join(missing)}",
                        "data": {"missing_fields": missing}
                    }),
                    content_type="application/json"
                )
            
            email = data['email']
            password = data['password']
            
            current = await self.request.app.store.admins.get_by_email(email)
            if current is None:
                return error_json_response(
                    http_status=403,
                    status="forbidden",
                    message="Invalid credentials",
                )

            if not bcrypt.checkpw(password.encode(), current.password.encode()):
                return error_json_response(
                    http_status=403,
                    status="forbidden",
                    message="Invalid credentials",
                )
            
            session_id = str(uuid.uuid4())
            await self.request.app["CookieStorage"].create_session(current.id, session_id)

            resp = json_response(
                data={"id": current.id, "email": current.email}
            )
            resp.set_cookie("session_id", session_id, expires=datetime.now() + timedelta(days=1))
            return resp
            
        except json.JSONDecodeError:
            raise HTTPBadRequest(
                text=json.dumps({
                    "status": "bad_request",
                    "message": "Invalid JSON format",
                    "data": {}
                }),
                content_type="application/json"
            )


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
