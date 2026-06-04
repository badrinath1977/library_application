from app.models.request_models import SampleRequest
from app.repository.sample_repository import SampleRepository


class SampleService:
    def __init__(self, repository: SampleRepository) -> None:
        self.repository = repository

    async def create_sample(self, payload: SampleRequest, user: dict | None):
        sample = await self.repository.create(payload)
        return {
            "id": sample.id,
            "name": sample.name,
            "description": sample.description,
            "created_at": sample.created_at.isoformat(),
            "created_by": user.get("sub") if isinstance(user, dict) else None,
        }
