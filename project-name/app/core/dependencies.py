from functools import lru_cache

from app.core.config import get_settings
from app.repository.customer_repository import CustomerRepository
from app.repository.sample_repository import SampleRepository
from app.service.customer_service import CustomerService
from app.service.external_api_service import ExternalApiService
from app.service.sample_service import SampleService
from app.service.token_service import TokenService


@lru_cache
def get_sample_repository() -> SampleRepository:
    return SampleRepository()


@lru_cache
def get_external_api_service() -> ExternalApiService:
    return ExternalApiService(settings=get_settings().external_api)


def get_sample_service() -> SampleService:
    return SampleService(
        repository=get_sample_repository(),
        external_api_service=get_external_api_service(),
    )


@lru_cache
def get_customer_repository() -> CustomerRepository:
    return CustomerRepository()


def get_customer_service() -> CustomerService:
    return CustomerService(repository=get_customer_repository())


def get_token_service() -> TokenService:
    return TokenService(settings=get_settings())
