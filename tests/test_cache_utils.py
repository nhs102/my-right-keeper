"""
Unit tests for cache_utils module.
"""

import pytest
from app.cache_utils import (
    get_query_keywords,
    calculate_similarity,
    find_similar_cached_query,
    VectorStoreCache,
)


class TestGetQueryKeywords:
    """Tests for get_query_keywords function."""

    def test_basic_extraction(self):
        """Test basic keyword extraction."""
        query = "퇴직금은 어떻게 계산하나요"
        keywords = get_query_keywords(query)

        assert "퇴직금은" in keywords
        assert "계산하나요" in keywords
        # Stopwords should be removed
        assert "은" not in keywords
        assert "어떻게" not in keywords  # "어떻게" is in stopwords list

    def test_empty_query(self):
        """Test empty query handling."""
        keywords = get_query_keywords("")
        assert len(keywords) == 0

    def test_single_character_removal(self):
        """Test that single characters are removed."""
        query = "퇴직금 계산 방법"
        keywords = get_query_keywords(query)

        # All should be included (no single chars)
        assert len(keywords) >= 2


class TestCalculateSimilarity:
    """Tests for calculate_similarity function."""

    def test_identical_queries(self):
        """Test similarity of identical queries."""
        query1 = "퇴직금 계산 방법"
        query2 = "퇴직금 계산 방법"

        similarity = calculate_similarity(query1, query2)
        assert similarity == 1.0

    def test_similar_queries(self):
        """Test similarity of similar queries."""
        query1 = "퇴직금 계산 방법"
        query2 = "퇴직금 계산 기준"

        similarity = calculate_similarity(query1, query2)
        assert 0.5 <= similarity < 1.0

    def test_different_queries(self):
        """Test similarity of different queries."""
        query1 = "퇴직금 계산"
        query2 = "주휴수당 지급"

        similarity = calculate_similarity(query1, query2)
        assert similarity < 0.5

    def test_empty_queries(self):
        """Test similarity with empty queries."""
        similarity = calculate_similarity("", "test")
        assert similarity == 0.0


class TestFindSimilarCachedQuery:
    """Tests for find_similar_cached_query function."""

    def test_find_similar(self):
        """Test finding similar cached query."""
        cached = {"퇴직금 계산 방법": "data1", "주휴수당 지급 기준": "data2"}

        result = find_similar_cached_query("퇴직금 계산 기준", cached, threshold=0.5)
        assert result == "퇴직금 계산 방법"

    def test_no_similar_found(self):
        """Test when no similar query is found."""
        cached = {"퇴직금 계산": "data1"}

        result = find_similar_cached_query("주휴수당 지급", cached, threshold=0.5)
        assert result is None

    def test_empty_cache(self):
        """Test with empty cache."""
        result = find_similar_cached_query("test query", {}, threshold=0.5)
        assert result is None


class TestVectorStoreCache:
    """Tests for VectorStoreCache class."""

    def test_initialization(self):
        """Test cache initialization."""
        cache = VectorStoreCache(max_size=3)
        assert cache.max_size == 3
        assert cache.size() == 0

    def test_put_and_get_exact(self):
        """Test putting and getting exact match."""
        cache = VectorStoreCache()

        cache.put("test query", "vector_store_data")
        result, key = cache.get("test query")

        assert result == "vector_store_data"
        assert key == "test query"

    def test_get_similar(self):
        """Test getting similar query."""
        cache = VectorStoreCache()

        cache.put("퇴직금 계산 방법", "vector_store_data")
        result, key = cache.get("퇴직금 계산 기준", threshold=0.5)

        assert result == "vector_store_data"
        assert key == "퇴직금 계산 방법"

    def test_cache_miss(self):
        """Test cache miss."""
        cache = VectorStoreCache()

        cache.put("퇴직금", "data")
        result, key = cache.get("주휴수당", threshold=0.5)

        assert result is None
        assert key is None

    def test_lru_eviction(self):
        """Test LRU eviction when cache is full."""
        cache = VectorStoreCache(max_size=2)

        cache.put("query1", "data1")
        cache.put("query2", "data2")
        cache.put("query3", "data3")  # Should evict query1

        assert cache.size() == 2
        result, _ = cache.get("query1")
        assert result is None  # query1 should be evicted

        result, _ = cache.get("query2")
        assert result == "data2"

        result, _ = cache.get("query3")
        assert result == "data3"

    def test_clear(self):
        """Test cache clearing."""
        cache = VectorStoreCache()

        cache.put("query1", "data1")
        cache.put("query2", "data2")

        cache.clear()
        assert cache.size() == 0

    def test_get_stats(self):
        """Test getting cache statistics."""
        cache = VectorStoreCache(max_size=5)

        cache.put("query1", "data1")
        cache.put("query2", "data2")

        stats = cache.get_stats()

        assert stats["size"] == 2
        assert stats["max_size"] == 5
        assert "query1" in stats["queries"]
        assert "query2" in stats["queries"]
