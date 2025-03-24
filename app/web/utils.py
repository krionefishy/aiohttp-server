from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response
from functools import wraps
from aiohttp.web_exceptions import HTTPUnauthorized

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