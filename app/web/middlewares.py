import json
import typing

from aiohttp.web_exceptions import HTTPUnprocessableEntity, HTTPInternalServerError, HTTPConflict, HTTPNotFound, \
    HTTPForbidden, HTTPUnauthorized, HTTPMethodNotAllowed, HTTPException
from aiohttp.web_middlewares import middleware
from aiohttp_apispec import validation_middleware

from app.web.utils import error_json_response

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
        response = await handler(request)
    except HTTPUnprocessableEntity as e:
        print("1")
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )
        

    return response
    # TODO: обработать все исключения-наследники HTTPException и отдельно Exception, как server error
    #  использовать текст из HTTP_ERROR_CODES


@middleware
async def error_auth_middleware(request: "Request", handler):
    try:
        return await handler(request)
    except HTTPUnauthorized as e:
        return error_json_response(
            http_status=401,
            status="unauthorized",
            message=e.reason,
            data={}
        )


@middleware
async def error_access_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPForbidden as e:
        return error_json_response(
            http_status=403,
            status=HTTP_ERROR_CODES[403],
            message=e.reason,
            data={},
        )

    return response


@middleware
async def error_not_found_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPNotFound as e:
        return error_json_response(
            http_status=404,
            status=HTTP_ERROR_CODES[404],
            message=e.reason,
            data={},
        )

    return response

@middleware
async def error_implementation_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPMethodNotAllowed as e:
        return error_json_response(
            http_status=405,
            status=HTTP_ERROR_CODES[405],
            message=e.reason,
            data={},
        )

    return response


@middleware
async def error_conflict_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPConflict as e:
        return error_json_response(
            http_status=409,
            status=HTTP_ERROR_CODES[409],
            message=e.reason,
            data={},
        )

    return response


@middleware
async def error_server_middleware(request: "Request", handler):
    try:
        response = await handler(request)
    except HTTPInternalServerError as e:
        return error_json_response(
            http_status=500,
            status=HTTP_ERROR_CODES[500],
            message=e.reason,
            data={},
        )

    return response




def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(error_auth_middleware)
    app.middlewares.append(error_access_middleware)
    app.middlewares.append(error_not_found_middleware)
    app.middlewares.append(error_implementation_middleware)
    app.middlewares.append(error_conflict_middleware)
    app.middlewares.append(error_server_middleware)
    #app.middlewares.append(error_unexpected)
    app.middlewares.append(validation_middleware)
