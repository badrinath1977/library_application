from app.models.request_models import SampleRequest
from app.repository.sample_repository import SampleRepository
from app.service.external_api_service import ExternalApiService


class SampleService:
    def __init__(
        self,
        repository: SampleRepository,
        external_api_service: ExternalApiService,
    ) -> None:
        self.repository = repository
        self.external_api_service = external_api_service

    async def create_sample(self, payload: SampleRequest, user: dict | None):
        sample = await self.repository.create(payload)
        return {
            "id": sample.id,
            "name": sample.name,
            "description": sample.description,
            "created_at": sample.created_at.isoformat(),
            "created_by": user.get("sub") if isinstance(user, dict) else None,
        }

    async def call_external_api(self, payload: dict):
        return await self.external_api_service.send(payload)
