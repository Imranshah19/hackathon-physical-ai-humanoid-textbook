"""
RAG retrieval service using Qdrant vector search.

Handles document retrieval for the chat agent using semantic search.
"""

import logging
from typing import Optional

from openai import AsyncOpenAI
from qdrant_client import models as qdrant_models

from src.config import get_settings
from src.db.qdrant import search_vectors, get_qdrant

logger = logging.getLogger(__name__)


class RetrievalService:
    """
    Service for retrieving relevant documentation chunks.

    Uses OpenAI embeddings + Qdrant vector search for semantic retrieval.
    """

    def __init__(
        self,
        top_k: int = 5,
        score_threshold: float = 0.7,
    ):
        """
        Initialize retrieval service.

        Args:
            top_k: Number of results to return.
            score_threshold: Minimum similarity score.
        """
        self.settings = get_settings()
        self.openai = AsyncOpenAI(api_key=self.settings.openai_api_key)
        self.top_k = top_k
        self.score_threshold = score_threshold

    async def retrieve(
        self,
        query: str,
        module_filter: Optional[str] = None,
        page_filter: Optional[str] = None,
    ) -> list[dict]:
        """
        Retrieve relevant document chunks for a query.

        Args:
            query: User's question or search query.
            module_filter: Optional module name to filter by (e.g., "module-1").
            page_filter: Optional page URL to prioritize.

        Returns:
            List of retrieved chunks with metadata.
        """
        try:
            # Generate query embedding
            query_embedding = await self._embed_query(query)

            # Build filter conditions
            filter_conditions = self._build_filter(module_filter, page_filter)

            # Search Qdrant
            results = await search_vectors(
                query_vector=query_embedding,
                limit=self.top_k,
                score_threshold=self.score_threshold,
                filter_conditions=filter_conditions,
            )

            # Format results
            chunks = []
            for result in results:
                payload = result.payload or {}
                chunks.append({
                    "content": payload.get("content", ""),
                    "source_url": payload.get("source_url", ""),
                    "section_title": payload.get("section_title", ""),
                    "module": payload.get("module", ""),
                    "score": result.score,
                    "chunk_index": payload.get("chunk_index", 0),
                })

            logger.info(f"Retrieved {len(chunks)} chunks for query: {query[:50]}...")
            return chunks

        except Exception as e:
            logger.error(f"Retrieval error: {e}")
            return []

    async def _embed_query(self, query: str) -> list[float]:
        """Generate embedding for a query string."""
        response = await self.openai.embeddings.create(
            model=self.settings.openai_embedding_model,
            input=query,
        )
        return response.data[0].embedding

    def _build_filter(
        self,
        module_filter: Optional[str],
        page_filter: Optional[str],
    ) -> Optional[qdrant_models.Filter]:
        """Build Qdrant filter conditions."""
        conditions = []

        if module_filter:
            conditions.append(
                qdrant_models.FieldCondition(
                    key="module",
                    match=qdrant_models.MatchValue(value=module_filter),
                )
            )

        if page_filter:
            conditions.append(
                qdrant_models.FieldCondition(
                    key="source_url",
                    match=qdrant_models.MatchValue(value=page_filter),
                )
            )

        if conditions:
            return qdrant_models.Filter(must=conditions)

        return None

    def format_context(self, chunks: list[dict], max_tokens: int = 2000) -> str:
        """
        Format retrieved chunks as context for the LLM.

        Args:
            chunks: Retrieved document chunks.
            max_tokens: Maximum tokens for context.

        Returns:
            Formatted context string.
        """
        if not chunks:
            return ""

        context_parts = []
        estimated_tokens = 0

        for chunk in chunks:
            chunk_text = f"""---
Source: {chunk['source_url']}
Section: {chunk['section_title']}
Module: {chunk['module']}

{chunk['content']}
---"""

            # Estimate tokens (4 chars per token)
            chunk_tokens = len(chunk_text) // 4

            if estimated_tokens + chunk_tokens > max_tokens:
                break

            context_parts.append(chunk_text)
            estimated_tokens += chunk_tokens

        return "\n\n".join(context_parts)
