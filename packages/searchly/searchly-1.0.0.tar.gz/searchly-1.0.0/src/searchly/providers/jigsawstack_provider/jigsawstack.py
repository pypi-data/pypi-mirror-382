"""Search tool using JigsawStack API."""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel


SafeSearchSetting = Literal["moderate", "strict", "off"]


class SearchResult(BaseModel):
    """Individual search result."""

    title: str
    url: str
    description: str
    content: str | None = None
    site_name: str | None = None
    site_long_name: str | None = None
    age: str | None = None
    language: str | None = None
    is_safe: bool = True
    favicon: str | None = None
    thumbnail: str | None = None
    snippets: list[str] | None = None


class AsyncJigsawStackClient:
    """Async client for JigsawStack API."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str = "https://api.jigsawstack.com/v1",
    ):
        """Initialize JigsawStack client.

        Args:
            api_key: JigsawStack API key. Defaults to JIGSAWSTACK_API_KEY env var.
            base_url: Base URL for the API.
        """
        self.api_key = api_key or os.getenv("JIGSAWSTACK_API_KEY")
        if not self.api_key:
            msg = "No API key provided. Set JIGSAWSTACK_API_KEY env var or pass api_key"
            raise ValueError(msg)

        self.base_url = base_url
        self.headers = {"Content-Type": "application/json", "x-api-key": self.api_key}

    async def search(
        self,
        query: str,
        *,
        ai_overview: bool = True,
        safe_search: SafeSearchSetting = "moderate",
        spell_check: bool = True,
        urls: list[str] | None = None,
    ) -> list[SearchResult]:
        """Execute search query using JigsawStack API.

        Args:
            query: Search query string
            ai_overview: Include AI-powered overview
            safe_search: Safe search level
            spell_check: Enable query spell checking
            urls: List of specific URLs to search

        Returns:
            Search results with metadata

        Raises:
            httpx.HTTPError: If API request fails
        """
        payload = {
            "query": query,
            "ai_overview": ai_overview,
            "safe_search": safe_search,
            "spell_check": spell_check,
        }

        if urls:
            payload["byo_urls"] = urls
        data = await anyenv.post_json(
            f"{self.base_url}/web/search",
            payload,
            headers=self.headers,
            return_type=dict,
        )

        return [SearchResult(**i) for i in data["results"]]


if __name__ == "__main__":
    import anyenv

    async def example():
        """Example usage of AsyncJigsawStackClient."""
        client = AsyncJigsawStackClient()
        results = await client.search("What is the capital of France?")
        print(results)

    anyenv.run_sync(example())
