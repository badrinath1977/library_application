from fastapi import APIRouter, Depends, Request

from app.core.dependencies import get_sample_service
from app.models.request_models import SampleRequest
from app.models.response_models import StandardResponse
from app.service.sample_service import SampleService
from app.utils.response_builder import build_success_response

router = APIRouter(tags=["Sample"])


@router.post("/", response_model=StandardResponse)
async def create_sample(
    payload: SampleRequest,
    request: Request,
    service: SampleService = Depends(get_sample_service),
):
    result = await service.create_sample(payload, user=request.state.user)
    return build_success_response(data=result, message="Sample processed successfully")
