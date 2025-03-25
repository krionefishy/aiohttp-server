from app.web.app import View
from app.web.utils import error_json_response, json_response
from aiohttp_apispec import docs, response_schema
from app.web.schemes import OkResponseSchema

import bcrypt

from aiohttp_session import new_session


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
            
            session = await new_session(request=self.request)
            session['admin_id'] = current.id
            session.max_age = self.request.app.config.session.lifetime

            
            resp = json_response(
                data={"id": current.id, "email": current.email}
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
