"""Tests for API client."""

import pytest
from unittest.mock import AsyncMock, patch

from forum_analyzer.collector.api_client import (
    ForumAPIClient,
    RateLimiter,
)


class TestRateLimiter:
    """Test rate limiter."""

    @pytest.mark.asyncio
    async def test_rate_limiting(self):
        """Test that rate limiter delays requests."""
        import time

        limiter = RateLimiter(rate=10.0)  # 10 requests per second

        start = time.time()
        for _ in range(3):
            await limiter.acquire()
        elapsed = time.time() - start

        # Should take at least 0.2 seconds (2 intervals at 0.1s each)
        assert elapsed >= 0.2


class TestForumAPIClient:
    """Test forum API client."""

    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test client context manager."""
        async with ForumAPIClient() as client:
            assert client.client is not None

    @pytest.mark.asyncio
    async def test_fetch_category_page(self):
        """Test fetching category page."""
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_request.return_value = AsyncMock(
                json=lambda: {
                    "topic_list": {"topics": []},
                    "category": {"name": "Test"},
                }
            )
            mock_request.return_value.raise_for_status = AsyncMock()

            async with ForumAPIClient() as client:
                data = await client.fetch_category_page(18, page=0)
                assert "topic_list" in data
                assert "category" in data

    @pytest.mark.asyncio
    async def test_fetch_topic(self):
        """Test fetching topic."""
        with patch("httpx.AsyncClient.request") as mock_request:
            mock_request.return_value = AsyncMock(
                json=lambda: {
                    "title": "Test Topic",
                    "post_stream": {"posts": []},
                }
            )
            mock_request.return_value.raise_for_status = AsyncMock()

            async with ForumAPIClient() as client:
                data = await client.fetch_topic(66)
                assert "title" in data
                assert "post_stream" in data
