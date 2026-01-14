"""
Qdrant Cloud vector database connection module.

Provides client management for vector similarity search.
"""

from typing import Optional

from qdrant_client import QdrantClient
from qdrant_client.http import models as qdrant_models

from src.config import get_settings

# Global Qdrant client
_client: Optional[QdrantClient] = None

# Vector configuration
VECTOR_SIZE = 1536  # text-embedding-3-small dimension
DISTANCE_METRIC = qdrant_models.Distance.COSINE


async def init_qdrant() -> None:
    """Initialize the Qdrant client and ensure collection exists."""
    global _client

    settings = get_settings()

    _client = QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key,
        timeout=30,
    )

    # Ensure collection exists
    collections = _client.get_collections().collections
    collection_names = [c.name for c in collections]

    if settings.qdrant_collection not in collection_names:
        _client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=qdrant_models.VectorParams(
                size=VECTOR_SIZE,
                distance=DISTANCE_METRIC,
            ),
            optimizers_config=qdrant_models.OptimizersConfigDiff(
                indexing_threshold=10000,
            ),
            hnsw_config=qdrant_models.HnswConfigDiff(
                m=16,
                ef_construct=100,
            ),
        )


async def close_qdrant() -> None:
    """Close the Qdrant client."""
    global _client

    if _client is not None:
        _client.close()
        _client = None


def get_qdrant() -> QdrantClient:
    """
    Get the Qdrant client.

    Returns:
        QdrantClient: The initialized Qdrant client.

    Raises:
        RuntimeError: If client not initialized.
    """
    if _client is None:
        raise RuntimeError("Qdrant not initialized. Call init_qdrant() first.")
    return _client


async def search_vectors(
    query_vector: list[float],
    limit: int = 5,
    score_threshold: float = 0.7,
    filter_conditions: Optional[qdrant_models.Filter] = None,
) -> list[qdrant_models.ScoredPoint]:
    """
    Search for similar vectors in the collection.

    Args:
        query_vector: The query embedding vector.
        limit: Maximum number of results.
        score_threshold: Minimum similarity score.
        filter_conditions: Optional filter for metadata.

    Returns:
        List of scored points with payload.
    """
    settings = get_settings()
    client = get_qdrant()

    results = client.search(
        collection_name=settings.qdrant_collection,
        query_vector=query_vector,
        limit=limit,
        score_threshold=score_threshold,
        query_filter=filter_conditions,
        with_payload=True,
    )

    return results


async def upsert_vectors(
    points: list[qdrant_models.PointStruct],
) -> None:
    """
    Upsert vectors into the collection.

    Args:
        points: List of points with id, vector, and payload.
    """
    settings = get_settings()
    client = get_qdrant()

    client.upsert(
        collection_name=settings.qdrant_collection,
        points=points,
        wait=True,
    )


async def delete_vectors(
    ids: list[str],
) -> None:
    """
    Delete vectors by ID.

    Args:
        ids: List of point IDs to delete.
    """
    settings = get_settings()
    client = get_qdrant()

    client.delete(
        collection_name=settings.qdrant_collection,
        points_selector=qdrant_models.PointIdsList(points=ids),
    )
