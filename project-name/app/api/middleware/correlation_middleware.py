from uuid import uuid4

from fastapi import Request

from app.utils.constants import CORRELATION_ID_HEADER


async def correlation_id_middleware(request: Request, call_next):
    correlation_id = request.headers.get(CORRELATION_ID_HEADER, str(uuid4()))
    request.state.correlation_id = correlation_id

    response = await call_next(request)
    response.headers[CORRELATION_ID_HEADER] = correlation_id
    return response
