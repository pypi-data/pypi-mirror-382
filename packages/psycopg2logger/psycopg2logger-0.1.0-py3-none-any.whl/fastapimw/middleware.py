import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapimw.context import current_request_path, current_request_method
import psycopg2logger


class SQLInterceptorMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path_token = current_request_path.set(request.url.path)
        http_method = current_request_method.set(request.method)
        try:
            response = await call_next(request)
        finally:
            current_request_path.reset(path_token)
        return response
