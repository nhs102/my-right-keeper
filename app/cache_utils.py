"""
Caching utilities for vector store management.
Provides session-based caching to improve response times for similar queries.
"""

import logging
from typing import Optional, Set
from datetime import datetime

logger = logging.getLogger(__name__)


def get_query_keywords(query: str) -> Set[str]:
    """
    Extract keywords from a query by removing common stopwords.

    Args:
        query: User query string

    Returns:
        Set of keywords
    """
    # Korean stopwords (common particles and auxiliary words)
    stopwords = {
        "은",
        "는",
        "이",
        "가",
        "을",
        "를",
        "의",
        "에",
        "에서",
        "로",
        "으로",
        "와",
        "과",
        "도",
        "만",
        "까지",
        "부터",
        "어떻게",
        "무엇",
        "언제",
        "어디",
        "왜",
        "어느",
        "있",
        "없",
        "하",
        "되",
        "수",
        "등",
        "및",
    }

    # Split and filter
    words = query.split()
    keywords = {word for word in words if len(word) > 1 and word not in stopwords}

    logger.debug(f"Extracted keywords from '{query}': {keywords}")
    return keywords


def calculate_similarity(query1: str, query2: str) -> float:
    """
    Calculate Jaccard similarity between two queries based on keywords.

    Args:
        query1: First query string
        query2: Second query string

    Returns:
        Similarity score between 0.0 and 1.0
    """
    keywords1 = get_query_keywords(query1)
    keywords2 = get_query_keywords(query2)

    if not keywords1 or not keywords2:
        return 0.0

    intersection = keywords1 & keywords2
    union = keywords1 | keywords2

    similarity = len(intersection) / len(union) if union else 0.0

    logger.debug(f"Similarity between '{query1}' and '{query2}': {similarity:.2f}")
    return similarity


def find_similar_cached_query(
    current_query: str, cached_queries: dict, threshold: float = 0.5
) -> Optional[str]:
    """
    Find the most similar cached query above the threshold.

    Args:
        current_query: Current user query
        cached_queries: Dictionary of cached queries
        threshold: Minimum similarity threshold (default: 0.5)

    Returns:
        Most similar cached query key, or None if no match found
    """
    best_match = None
    best_similarity = 0.0

    for cached_query in cached_queries.keys():
        similarity = calculate_similarity(current_query, cached_query)

        if similarity > best_similarity and similarity >= threshold:
            best_similarity = similarity
            best_match = cached_query

    if best_match:
        logger.info(
            f"Found similar cached query: '{best_match}' (similarity: {best_similarity:.2f})"
        )
    else:
        logger.info(f"No similar cached query found for: '{current_query}'")

    return best_match


class VectorStoreCache:
    """
    Manages vector store caching with LRU eviction policy.
    """

    def __init__(self, max_size: int = 5):
        """
        Initialize cache.

        Args:
            max_size: Maximum number of cached items
        """
        self.max_size = max_size
        self.cache = {}
        self.timestamps = {}
        logger.info(f"Initialized VectorStoreCache with max_size={max_size}")

    def get(self, query: str, threshold: float = 0.5):
        """
        Get cached vector store for a query or similar query.

        Args:
            query: User query
            threshold: Similarity threshold for cache hit

        Returns:
            Tuple of (vector_store, cache_key) or (None, None)
        """
        # Exact match
        if query in self.cache:
            logger.info(f"Cache hit (exact): '{query}'")
            self.timestamps[query] = datetime.now()
            return self.cache[query], query

        # Similar match
        similar_query = find_similar_cached_query(query, self.cache, threshold)
        if similar_query:
            logger.info(f"Cache hit (similar): '{similar_query}' for '{query}'")
            self.timestamps[similar_query] = datetime.now()
            return self.cache[similar_query], similar_query

        logger.info(f"Cache miss: '{query}'")
        return None, None

    def put(self, query: str, vector_store):
        """
        Add vector store to cache.

        Args:
            query: User query key
            vector_store: Vector store to cache
        """
        # Evict oldest if cache is full
        if len(self.cache) >= self.max_size:
            oldest_query = min(self.timestamps.items(), key=lambda x: x[1])[0]
            logger.info(f"Cache full, evicting oldest: '{oldest_query}'")
            del self.cache[oldest_query]
            del self.timestamps[oldest_query]

        self.cache[query] = vector_store
        self.timestamps[query] = datetime.now()
        logger.info(
            f"Cached vector store for: '{query}' (cache size: {len(self.cache)})"
        )

    def clear(self):
        """Clear all cached items."""
        self.cache.clear()
        self.timestamps.clear()
        logger.info("Cache cleared")

    def size(self) -> int:
        """Get current cache size."""
        return len(self.cache)

    def get_stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "queries": list(self.cache.keys()),
        }
