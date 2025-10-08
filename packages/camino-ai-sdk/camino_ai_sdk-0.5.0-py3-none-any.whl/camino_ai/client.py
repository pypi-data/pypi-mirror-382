"""Main client class for the Camino AI SDK."""

import asyncio
from typing import Any, Optional, Union

import httpx
from httpx import AsyncClient, Client, Response

from .models import (
    APIError,
    AuthenticationError,
    ContextRequest,
    ContextResponse,
    JourneyRequest,
    JourneyResponse,
    QueryRequest,
    QueryResponse,
    RateLimitError,
    RelationshipRequest,
    RelationshipResponse,
    RouteRequest,
    RouteResponse,
    SearchRequest,
    SearchResponse,
)


class CaminoAI:
    """
    Camino AI client for location intelligence and spatial reasoning.

    This client provides both synchronous and asynchronous methods for
    interacting with the Camino AI API.

    Args:
        api_key: Your Camino AI API key
        base_url: API base URL (defaults to production)
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
        retry_backoff: Backoff multiplier for retries
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.getcamino.ai",
        timeout: float = 30.0,
        max_retries: int = 3,
        retry_backoff: float = 1.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff

        self._headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
            "User-Agent": "camino-ai-python/0.1.0",
        }

        # Sync client (created lazily)
        self._sync_client: Optional[Client] = None

        # Async client (created lazily)
        self._async_client: Optional[AsyncClient] = None

    @property
    def sync_client(self) -> Client:
        """Get or create synchronous HTTP client."""
        if self._sync_client is None:
            self._sync_client = Client(
                headers=self._headers,
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._sync_client

    @property
    def async_client(self) -> AsyncClient:
        """Get or create asynchronous HTTP client."""
        if self._async_client is None:
            self._async_client = AsyncClient(
                headers=self._headers,
                timeout=self.timeout,
                follow_redirects=True,
            )
        return self._async_client

    def _handle_response(self, response: Response) -> dict[str, Any]:
        """Handle HTTP response and raise appropriate exceptions."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code

            try:
                error_data = e.response.json()
                message = error_data.get("message", str(e))
            except Exception:
                message = str(e)

            if status_code == 401:
                raise AuthenticationError(message, status_code, error_data) from e
            elif status_code == 429:
                retry_after = e.response.headers.get("Retry-After")
                retry_seconds = int(retry_after) if retry_after else None
                raise RateLimitError(message, retry_seconds) from e
            else:
                raise APIError(message, status_code, error_data) from e
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {str(e)}") from e

    def _make_request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:  # type: ignore[misc,return]
        """Make synchronous HTTP request with retries."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries + 1):
            try:
                response = self.sync_client.request(method, url, **kwargs)
                return self._handle_response(response)
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt == self.max_retries:
                    raise APIError(
                        f"Request failed after {self.max_retries + 1} attempts: {str(e)}"
                    ) from e

                # Exponential backoff
                import time

                time.sleep(self.retry_backoff * (2**attempt))

    async def _make_async_request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:  # type: ignore[misc,return]
        """Make asynchronous HTTP request with retries."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(self.max_retries + 1):
            try:
                response = await self.async_client.request(method, url, **kwargs)
                return self._handle_response(response)
            except (httpx.RequestError, httpx.TimeoutException) as e:
                if attempt == self.max_retries:
                    raise APIError(
                        f"Request failed after {self.max_retries + 1} attempts: {str(e)}"
                    ) from e

                # Exponential backoff
                await asyncio.sleep(self.retry_backoff * (2**attempt))

    # Query methods
    def query(self, query: Union[str, QueryRequest]) -> QueryResponse:
        """
        Broad area-based query for points of interest using natural language.

        Args:
            query: Natural language query string or QueryRequest object

        Returns:
            QueryResponse with search results
        """
        if isinstance(query, str):
            query = QueryRequest(query=query)  # type: ignore[call-arg]

        data = self._make_request(
            "GET", "/query", params=query.model_dump(exclude_none=True)
        )
        return QueryResponse.model_validate(data)

    async def query_async(self, query: Union[str, QueryRequest]) -> QueryResponse:
        """Async version of query method."""
        if isinstance(query, str):
            query = QueryRequest(query=query)  # type: ignore[call-arg]

        data = await self._make_async_request(
            "GET", "/query", params=query.model_dump(exclude_none=True)
        )
        return QueryResponse.model_validate(data)

    # Search methods
    def search(self, query: Union[str, SearchRequest]) -> SearchResponse:
        """
        Search for places using Nominatim with flexible query options.

        Supports two modes:
        1. Free-form search: Pass a string or SearchRequest with 'query' parameter
        2. Structured search: Pass SearchRequest with address components

        Examples:
            # Free-form search (backward compatible)
            client.search("Eiffel Tower")

            # Structured search for restaurants in a city
            client.search(SearchRequest(
                amenity="restaurant",
                city="Paris",
                country="France",
                limit=10
            ))

            # Search by specific address
            client.search(SearchRequest(
                street="123 Main Street",
                city="New York",
                state="New York"
            ))

        Args:
            query: Search query string or SearchRequest object with either
                   free-form query or structured address parameters

        Returns:
            SearchResponse with search results including address details
        """
        if isinstance(query, str):
            query = SearchRequest(query=query)  # type: ignore[call-arg]

        data = self._make_request(
            "POST", "/search", params=query.model_dump(exclude_none=True)
        )
        return SearchResponse.model_validate({"results": data})

    async def search_async(self, query: Union[str, SearchRequest]) -> SearchResponse:
        """
        Async version of search method with flexible query options.

        See search() method for detailed documentation and examples.

        Args:
            query: Search query string or SearchRequest object

        Returns:
            SearchResponse with search results including address details
        """
        if isinstance(query, str):
            query = SearchRequest(query=query)  # type: ignore[call-arg]

        data = await self._make_async_request(
            "POST", "/search", params=query.model_dump(exclude_none=True)
        )
        return SearchResponse.model_validate({"results": data})

    # Relationship methods
    def relationship(self, request: RelationshipRequest) -> RelationshipResponse:
        """
        Calculate spatial relationships between points.

        Args:
            request: RelationshipRequest with location data

        Returns:
            RelationshipResponse with spatial relationship info
        """
        data = self._make_request(
            "POST", "/relationship", json=request.model_dump(exclude_none=True)
        )
        return RelationshipResponse.model_validate(data)

    async def relationship_async(
        self, request: RelationshipRequest
    ) -> RelationshipResponse:
        """Async version of relationship method."""
        data = await self._make_async_request(
            "POST", "/relationship", json=request.model_dump(exclude_none=True)
        )
        return RelationshipResponse.model_validate(data)

    # Context methods
    def context(self, request: ContextRequest) -> ContextResponse:
        """
        Get contextual information about a location.

        Args:
            request: ContextRequest with location and parameters

        Returns:
            ContextResponse with location context
        """
        data = self._make_request(
            "POST", "/context", json=request.model_dump(exclude_none=True)
        )
        return ContextResponse.model_validate(data)

    async def context_async(self, request: ContextRequest) -> ContextResponse:
        """Async version of context method."""
        data = await self._make_async_request(
            "POST", "/context", json=request.model_dump(exclude_none=True)
        )
        return ContextResponse.model_validate(data)

    # Journey methods
    def journey(self, request: JourneyRequest) -> JourneyResponse:
        """
        Plan multi-waypoint journeys with optimization.

        Args:
            request: JourneyRequest with waypoints and constraints

        Returns:
            JourneyResponse with optimized journey plan
        """
        data = self._make_request(
            "POST", "/journey", json=request.model_dump(exclude_none=True)
        )
        return JourneyResponse.model_validate(data)

    async def journey_async(self, request: JourneyRequest) -> JourneyResponse:
        """Async version of journey method."""
        data = await self._make_async_request(
            "POST", "/journey", json=request.model_dump(exclude_none=True)
        )
        return JourneyResponse.model_validate(data)

    # Route methods
    def route(self, request: RouteRequest) -> RouteResponse:
        """
        Calculate routes between two points.

        Args:
            request: RouteRequest with start/end points and options

        Returns:
            RouteResponse with route information
        """
        data = self._make_request(
            "GET", "/route", params=request.model_dump(exclude_none=True)
        )
        return RouteResponse.model_validate(data)

    async def route_async(self, request: RouteRequest) -> RouteResponse:
        """Async version of route method."""
        data = await self._make_async_request(
            "GET", "/route", params=request.model_dump(exclude_none=True)
        )
        return RouteResponse.model_validate(data)

    def close(self) -> None:
        """Close synchronous client."""
        if self._sync_client:
            self._sync_client.close()

    async def aclose(self) -> None:
        """Close asynchronous client."""
        if self._async_client:
            await self._async_client.aclose()

    def __enter__(self) -> "CaminoAI":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Context manager exit."""
        self.close()

    async def __aenter__(self) -> "CaminoAI":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore[no-untyped-def]
        """Async context manager exit."""
        await self.aclose()
