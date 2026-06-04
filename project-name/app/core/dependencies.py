from functools import lru_cache

from app.repository.customer_repository import CustomerRepository
from app.repository.sample_repository import SampleRepository
from app.service.customer_service import CustomerService
from app.service.sample_service import SampleService


@lru_cache
def get_sample_repository() -> SampleRepository:
    return SampleRepository()


def get_sample_service() -> SampleService:
    return SampleService(repository=get_sample_repository())


@lru_cache
def get_customer_repository() -> CustomerRepository:
    return CustomerRepository()


def get_customer_service() -> CustomerService:
    return CustomerService(repository=get_customer_repository())
