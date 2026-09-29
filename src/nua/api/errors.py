import logging

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from nua.api.schemas import ErrorResponse
from nua.domain import DomainException

_logger = logging.getLogger(__name__)


async def _handle_domain_exception(request: Request, exception: DomainException) -> JSONResponse:
    _logger.warning(f'Domain exception raised: {exception}')

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=ErrorResponse(detail=str(exception)).model_dump()
    )


def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(DomainException, _handle_domain_exception)
