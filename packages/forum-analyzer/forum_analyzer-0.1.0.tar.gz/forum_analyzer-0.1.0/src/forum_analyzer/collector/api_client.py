"""Async API client for Discourse Forum."""

import asyncio
import logging
from typing import Any, Dict, Optional
from datetime import datetime

import httpx
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(self, rate: float = 1.0):
        """Initialize rate limiter.

        Args:
            rate: Requests per second (default: 1.0)
        """
        self.rate = rate
        self.interval = 1.0 / rate
        self.last_request = 0.0

    async def acquire(self) -> None:
        """Acquire permission to make a request."""
        now = asyncio.get_event_loop().time()
        time_since_last = now - self.last_request

        if time_since_last < self.interval:
            await asyncio.sleep(self.interval - time_since_last)

        self.last_request = asyncio.get_event_loop().time()


class ForumAPIClient:
    """Async HTTP client for Discourse Forum API."""

    def __init__(
        self,
        base_url: str,
        category_path: str,
        rate_limit: float = 1.0,
        timeout: float = 30.0,
        max_retries: int = 3,
    ):
        """Initialize API client.

        Args:
            base_url: Base URL for the forum API
            category_path: URL path segment for categories (e.g., "c" or "t")
            rate_limit: Requests per second (default: 1.0)
            timeout: Request timeout in seconds (default: 30.0)
            max_retries: Maximum retry attempts (default: 3)
        """
        self.base_url = base_url
        self.rate_limiter = RateLimiter(rate=rate_limit)
        self.timeout = timeout
        self.max_retries = max_retries
        self.category_path = category_path
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self) -> "ForumAPIClient":
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            follow_redirects=True,
            headers={
                "User-Agent": "Discourse-Forum-Analyzer/0.1.0",
                "Accept": "application/json",
            },
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()

    @retry(
        retry=retry_if_exception_type(
            (httpx.HTTPStatusError, httpx.TimeoutException)
        ),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        stop=stop_after_attempt(3),
    )
    async def _request(
        self, method: str, url: str, **kwargs
    ) -> Dict[str, Any]:
        """Make HTTP request with retry logic.

        Args:
            method: HTTP method
            url: Request URL
            **kwargs: Additional request parameters

        Returns:
            JSON response data

        Raises:
            httpx.HTTPError: On HTTP errors
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use async context.")

        await self.rate_limiter.acquire()

        logger.debug(f"Making {method} request to {url}")
        response = await self.client.request(method, url, **kwargs)

        # Log redirect information
        if response.history:
            redirect_count = len(response.history)
            logger.info(f"Request redirected: {redirect_count} redirect(s)")
            for i, redirect in enumerate(response.history):
                status = redirect.status_code
                logger.info(f"  Redirect {i+1}: {redirect.url} -> {status}")
            logger.info(f"  Final URL: {response.url}")

        response.raise_for_status()

        return response.json()

    async def fetch_category_page(
        self, category_id: int, page: int = 0
    ) -> Dict[str, Any]:
        """Fetch a page of topics from a category.

        Args:
            category_id: Category ID
            page: Page number (0-indexed, default: 0)

        Returns:
            Category page JSON data
        """
        url = f"/{self.category_path}/{category_id}.json"
        params = {"page": page} if page > 0 else {}

        logger.info(f"Fetching category {category_id}, page {page}")
        data = await self._request("GET", url, params=params)

        return data

    async def fetch_topic(self, topic_id: int) -> Dict[str, Any]:
        """Fetch a topic with all posts.

        Args:
            topic_id: Topic ID

        Returns:
            Topic JSON data
        """
        url = f"/t/{topic_id}.json"

        logger.info(f"Fetching topic {topic_id}")
        data = await self._request("GET", url)

        return data

    async def fetch_category_metadata(
        self, category_id: int
    ) -> Dict[str, Any]:
        """Fetch category metadata (first page).

        Args:
            category_id: Category ID

        Returns:
            Category metadata
        """
        data = await self.fetch_category_page(category_id, page=0)

        return {
            "id": category_id,
            "name": data.get("category", {}).get("name", ""),
            "slug": data.get("category", {}).get("slug", ""),
            "description": data.get("category", {}).get(
                "description_text", ""
            ),
            "topic_count": data.get("category", {}).get("topic_count", 0),
            "post_count": data.get("category", {}).get("post_count", 0),
            "last_scraped_at": datetime.utcnow(),
        }


async def main():
    """Example usage."""
    async with ForumAPIClient(rate_limit=1.0) as client:
        # Fetch category metadata
        category_data = await client.fetch_category_metadata(18)
        print(f"Category: {category_data['name']}")

        # Fetch first page
        page_data = await client.fetch_category_page(18, page=0)
        print(f"Topics on page 0: {len(page_data['topic_list']['topics'])}")

        # Fetch a specific topic
        topic_data = await client.fetch_topic(66)
        print(f"Topic: {topic_data['title']}")
        print(f"Posts: {len(topic_data['post_stream']['posts'])}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
