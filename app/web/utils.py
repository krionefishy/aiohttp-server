from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response
from functools import wraps
from aiohttp.web_exceptions import HTTPUnauthorized
from typing import Callable, Any
from aiohttp.web import HTTPBadRequest
import json

def json_response(data: dict | None = None, status: str = "ok") -> Response:
    if data is None:
        data = {}

    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )


def error_json_response(
    http_status: int,
    status: str = "bad_request",
    message: str | None = None,
    data: dict | None = None,
):
    return aiohttp_json_response(
        data={
            "status": status,
            "message": message,
            "data": data
        }
    )

def auth_required(handler):
    @wraps(handler)
    async def wrapper(self, *args, **kwargs):
        session_id = self.request.cookies.get("session_id")
        if not session_id:
            raise HTTPUnauthorized(reason="No session cookie found")

        cookie_storage = self.request.app.get("CookieStorage")
        if not cookie_storage or not await cookie_storage.is_valid_cookie(session_id):
            raise HTTPUnauthorized(reason="Invalid session cookie")

        admin_id = await cookie_storage.get_admin_id_by_session(session_id)
        admin = await self.request.app.store.admins.get_by_id(admin_id)
        if not admin:
            raise HTTPUnauthorized(reason="Admin not found")

        self.request.admin = admin
        return await handler(self, *args, **kwargs)
    return wrapper


from typing import Callable, TypeVar, Any
from marshmallow import ValidationError

T = TypeVar('T')

def validate_request(schema_class=None, *, required_fields: list[str] = None):
    """
    Декоратор для валидации входящих данных
    
    :param schema_class: Класс схемы Marshmallow для валидации
    :param required_fields: Список обязательных полей (если не используется schema_class)
    """
    def decorator(handler: Callable[..., T]) -> Callable[..., T]:
        @wraps(handler)
        async def wrapper(self, *args, **kwargs) -> T:
            try:
                data = await self.request.json()
                
                # Валидация через схему Marshmallow
                if schema_class:
                    schema = schema_class()
                    validated_data = schema.load(data)
                    self.request['data'] = validated_data
                # Или простая проверка обязательных полей
                elif required_fields:
                    missing_fields = [field for field in required_fields if field not in data]
                    if missing_fields:
                        raise HTTPBadRequest(
                            reason=f"Missing required fields: {', '.join(missing_fields)}"
                        )
                    self.request['data'] = data
                
                return await handler(self, *args, **kwargs)
            
            except ValidationError as e:
                raise HTTPBadRequest(
                    reason="Validation error",
                    text=json.dumps({
                        "status": "bad_request",
                        "message": "Invalid data",
                        "data": e.messages
                    }),
                    content_type="application/json"
                )
            except json.JSONDecodeError:
                raise HTTPBadRequest(
                    reason="Invalid JSON",
                    text=json.dumps({
                        "status": "bad_request",
                        "message": "Invalid JSON format",
                        "data": {}
                    }),
                    content_type="application/json"
                )
        
        return wrapper
    return decorator