from app.models.absence_request import AbsenceSearchRequest
from app.models.absence_response import Pagination
from app.repositories.absence_repository import AbsenceRepository


def test_request_aliases_and_defaults() -> None:
    request = AbsenceSearchRequest.model_validate(
        {
            "personNumber": "41556",
            "absenceType": "Sick Time",
            "approvalStatusCd": "APPROVED",
            "startDateFrom": "2025-01-01",
            "startDateTo": "2025-12-31",
        }
    )
    assert request.person_number == "41556"
    assert request.page_number == 1
    assert request.page_size == 20


def test_repository_parameter_count_matches_procedure_call() -> None:
    request = AbsenceSearchRequest(personNumber="41556")
    assert len(AbsenceRepository._params(request)) == 40
    assert AbsenceRepository.COMMAND.count("?") == 40


def test_pagination_aliases() -> None:
    pagination = Pagination(totalRecords=1, currentPage=1, pageSize=20, totalPages=1)
    assert pagination.model_dump(by_alias=True)["totalRecords"] == 1

