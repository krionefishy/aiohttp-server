import json
import typing

from aiohttp.web_exceptions import HTTPUnprocessableEntity, HTTPException, HTTPUnauthorized
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from app.web.utils import error_json_response
import logging
logging.basicConfig(level=logging.INFO)

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}


@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        return await handler(request)
        
    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
    except HTTPException as e:
        status_code = e.status_code
        
        try:
            error_data = json.loads(e.text)
        except:
            error_data = {"message": e.reason}
        logging.error(f"occured an error {e}, code {status_code}, err_data {error_data}")
        return error_json_response(
            http_status=status_code,
            status=HTTP_ERROR_CODES.get(status_code, "unknown_error"),
            message=e.reason,
            data=error_data
        )
    except Exception as e:
        logging.error(f"occured an error {e}")
        return error_json_response(
            http_status=500,
            status=HTTP_ERROR_CODES[500],
            message=str(e),
            data={}
        )
    
"""@middleware
async def auth_middleware(request: "Request", handler):
    PUBLIC_PATHS = ["/admin.login"]

    if request.path in PUBLIC_PATHS:
        return await handler(request)

    session_id = request.cookies.get("session_id")
    if not session_id:
        raise HTTPUnauthorized(
            text=json.dumps({
                "status": "unauthorized",
                "message": "Session cookie is required"
            }),
            content_type="application/json"
        )
    if not await request.app.cookie_storage.is_valid_cookie(session_id):
        raise HTTPUnauthorized(
            text=json.dumps({
                "status": "unauthorized",
                "message": "Invalid session"
            }),
            content_type="application/json"
        )

    return await handler(request)"""


def setup_middlewares(app: "Application"):
    #app.middlewares.append(auth_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
