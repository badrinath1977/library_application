from fastapi import APIRouter, Depends

from app.core.dependencies import get_token_service
from app.models.request_models import TestTokenRequest
from app.models.response_models import StandardResponse
from app.service.token_service import TokenService
from app.utils.response_builder import build_success_response

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/test-token", response_model=StandardResponse)
async def create_test_token(
    payload: TestTokenRequest,
    service: TokenService = Depends(get_token_service),
):
    token = service.create_test_token(payload)
    return build_success_response(data=token, message="Test token created successfully")
