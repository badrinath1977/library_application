from app.core.exceptions import AppException
from app.models.db_models import CustomerDBModel
from app.models.request_models import CustomerCreateRequest, CustomerUpdateRequest
from app.repository.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    async def create_customer(self, payload: CustomerCreateRequest) -> dict:
        customer = await self.repository.create(payload)
        return self._to_response(customer)

    async def get_customer(self, customer_id: int) -> dict:
        customer = await self.repository.get_by_id(customer_id)
        if customer is None:
            raise AppException("Customer not found", status_code=404, error_code="CUSTOMER_NOT_FOUND")
        return self._to_response(customer)

    async def list_customers(self) -> list[dict]:
        customers = await self.repository.list_all()
        return [self._to_response(customer) for customer in customers]

    async def update_customer(self, customer_id: int, payload: CustomerUpdateRequest) -> dict:
        customer = await self.repository.update(customer_id, payload)
        if customer is None:
            raise AppException("Customer not found", status_code=404, error_code="CUSTOMER_NOT_FOUND")
        return self._to_response(customer)

    async def delete_customer(self, customer_id: int) -> dict:
        deleted = await self.repository.delete(customer_id)
        if not deleted:
            raise AppException("Customer not found", status_code=404, error_code="CUSTOMER_NOT_FOUND")
        return {"id": customer_id, "deleted": True}

    @staticmethod
    def _to_response(customer: CustomerDBModel) -> dict:
        return {
            "id": customer.id,
            "first_name": customer.first_name,
            "last_name": customer.last_name,
            "email": customer.email,
            "phone": customer.phone,
            "created_at": customer.created_at.isoformat() if customer.created_at else None,
            "updated_at": customer.updated_at.isoformat() if customer.updated_at else None,
        }
