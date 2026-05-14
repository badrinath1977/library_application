"""Retrieval augmented generation service."""

from __future__ import annotations

import logging

from llm_platform_library.client import LLMClient
from llm_platform_library.exceptions import LLMPlatformLibraryError, RAGError
from llm_platform_library.logger import get_bootstrap_logger
from llm_platform_library.models import RAGDocument, RAGResponse


class RAGService:
    """Build RAG prompts from retrieved documents and call an LLM client."""

    def __init__(
        self,
        llm_client: LLMClient,
        logger: logging.Logger | None = None,
    ) -> None:
        self._llm_client = llm_client
        self._logger = logger or get_bootstrap_logger()

    def generate_answer(self, query: str, documents: list[RAGDocument]) -> RAGResponse:
        """Generate a grounded answer for a query and retrieved documents."""

        self._logger.debug(
            "event=rag_generate_answer_start document_count=%d",
            len(documents),
        )
        if not isinstance(query, str) or not query.strip():
            self._logger.exception("event=rag_invalid_query status=failure")
            raise RAGError("Query must be a non-empty string.")

        try:
            context = self.build_context(documents)
            prompt = (
                "Answer the question using only the provided context.\n\n"
                f"Context:\n{context}\n\n"
                f"Question: {query}\n"
                "Answer:"
            )
            llm_response = self._llm_client.generate_response(prompt)
            source_ids = tuple(document.document_id for document in documents)
            self._logger.info(
                "event=rag_answer_generated status=success source_count=%d",
                len(source_ids),
            )
            return RAGResponse(
                answer=llm_response.content,
                source_document_ids=source_ids,
                llm_response=llm_response,
            )
        except RAGError:
            raise
        except LLMPlatformLibraryError as exc:
            self._logger.exception("event=rag_generation_failed status=failure")
            raise RAGError("RAG answer generation failed.") from exc
        finally:
            self._logger.debug("event=rag_generate_answer_end")

    def build_context(self, documents: list[RAGDocument]) -> str:
        """Build context text from retrieved documents."""

        self._logger.debug(
            "event=rag_build_context_start document_count=%d",
            len(documents),
        )
        context_parts = [
            f"[{document.document_id}]\n{document.content.strip()}"
            for document in documents
            if document.content.strip()
        ]
        context = "\n\n".join(context_parts)
        self._logger.debug("event=rag_build_context_end")
        return context
