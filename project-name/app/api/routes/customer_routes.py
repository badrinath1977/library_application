from fastapi import APIRouter, Depends

from app.core.dependencies import get_customer_service
from app.models.request_models import CustomerCreateRequest, CustomerUpdateRequest
from app.models.response_models import StandardResponse
from app.service.customer_service import CustomerService
from app.utils.response_builder import build_success_response

router = APIRouter(prefix="/customer", tags=["Customer"])


@router.post("/", response_model=StandardResponse, status_code=201)
async def create_customer(
    payload: CustomerCreateRequest,
    service: CustomerService = Depends(get_customer_service),
):
    result = await service.create_customer(payload)
    return build_success_response(data=result, message="Customer created successfully")


@router.get("/", response_model=StandardResponse)
async def list_customers(service: CustomerService = Depends(get_customer_service)):
    result = await service.list_customers()
    return build_success_response(data=result, message="Customers fetched successfully")


@router.get("/{customer_id}", response_model=StandardResponse)
async def get_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service),
):
    result = await service.get_customer(customer_id)
    return build_success_response(data=result, message="Customer fetched successfully")


@router.put("/{customer_id}", response_model=StandardResponse)
async def update_customer(
    customer_id: int,
    payload: CustomerUpdateRequest,
    service: CustomerService = Depends(get_customer_service),
):
    result = await service.update_customer(customer_id, payload)
    return build_success_response(data=result, message="Customer updated successfully")


@router.delete("/{customer_id}", response_model=StandardResponse)
async def delete_customer(
    customer_id: int,
    service: CustomerService = Depends(get_customer_service),
):
    result = await service.delete_customer(customer_id)
    return build_success_response(data=result, message="Customer deleted successfully")
