import uuid

from starlette.middleware.base import BaseHTTPMiddleware

from app.core.request_context import request_id_ctx_var


class RequestIDMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request, call_next):

        request_id = str(uuid.uuid4())

        request_id_ctx_var.set(request_id)

        response = await call_next(request)

        response.headers["X-Request-ID"] = request_id

        return response