"""Ticket creation service."""

from __future__ import annotations

import hashlib
import logging

from app.core.config import Settings
from app.core.exceptions import TicketServiceError
from app.models.response_models import ErrorAnalysisResponse, TicketResponse

logger = logging.getLogger(__name__)


class TicketService:
    """Create tickets through a provider interface."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def create_ticket(self, error: ErrorAnalysisResponse) -> TicketResponse:
        """Create a ticket for an analyzed error."""

        try:
            if self._settings.ticket_provider != "mock":
                raise TicketServiceError(
                    f"Ticket provider '{self._settings.ticket_provider}' is not implemented."
                )
            digest = hashlib.sha256(error.id.encode("utf-8")).hexdigest()[:8].upper()
            return TicketResponse(
                created=True,
                ticket_id=f"{self._settings.ticket_project_key}-{digest}",
            )
        except TicketServiceError as exc:
            logger.exception("Ticket creation failed for error_id=%s", error.id)
            return TicketResponse(created=False, error=str(exc))

