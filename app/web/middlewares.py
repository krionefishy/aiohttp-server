import json
import typing

from aiohttp.web_exceptions import HTTPUnprocessableEntity, HTTPException, HTTPUnauthorized
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware
from aiohttp_session import get_session
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
    
@middleware
async def auth_middleware(request, handler):
    if request.path in ['/admin.login', '/login']:
        return await handler(request)
    
    try:
        session = await get_session(request)
        admin_id = session.get('admin_id')
        
        if not admin_id:
            raise HTTPUnauthorized(
                text=json.dumps({
                    "status": "unauthorized",
                    "message": "Authentication required"
                }),
                content_type="application/json"
            )
            
        admin = await request.app.store.admins.get_by_id(admin_id)
        if not admin:
            raise HTTPUnauthorized(
                text=json.dumps({
                    "status": "unauthorized",
                    "message": "Invalid credentials"
                }),
                content_type="application/json"
            )
            
        request.admin = admin
        return await handler(request)
        
    except HTTPException as e:
        if not hasattr(e, 'content_type') or e.content_type != 'application/json':
            e.content_type = 'application/json'
        raise


def setup_middlewares(app: "Application"):
    app.middlewares.append(auth_middleware)
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
