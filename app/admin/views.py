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
import json
from aiohttp.web_exceptions import HTTPBadRequest


class AdminLoginView(View):
    @response_schema(OkResponseSchema, 200)
    async def post(self):
            data = await self.request.json()
            
            if 'email' not in data or 'password' not in data:
                missing = []
                if 'email' not in data: missing.append('email')
                if 'password' not in data: missing.append('password')
                return error_json_response(
                    http_status=400,
                    status="bad_request",
                    message="Unprocessable Entity",
                    data={"json": {field: ["Missing data for required field."] for field in missing}}
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
            await self.request.app.cookie_storage.create_session(current.id, session_id)
            """ls = await self.request.app.cookie_storage.list_cookies_debug()
            print(ls)"""
            resp = json_response(
                data={"id": current.id, "email": current.email}
            )
            resp.set_cookie(
                 "session_id", 
                 session_id, 
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
    async def get(self):
        admin = {
            "id": self.request.admin.id,
            "email": self.request.admin.email
        }
        
        resp = json_response(
            data=admin
        )

        return resp
