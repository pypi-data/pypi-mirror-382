"""
Utility functions for caching and retry logic.

Implements TTL caching with stale-while-revalidate support.
"""

import asyncio
import time
from typing import Any, Dict, Optional

from .types import CacheOptions, Resolver


class TTL:
    """Pre-defined TTL constants for convenience (in seconds)."""

    short = 30  # 30 seconds
    minute = 60  # 1 minute
    minutes5 = 5 * 60  # 5 minutes
    minutes15 = 15 * 60  # 15 minutes
    hour = 60 * 60  # 1 hour
    hours6 = 6 * 60 * 60  # 6 hours
    day = 24 * 60 * 60  # 24 hours


class CachedResolver:
    """
    Wrapper that caches resolver results with TTL and stale-while-revalidate support.

    This implements the same caching strategy as the TypeScript version:
    - Age < TTL: Return cached data (fresh)
    - TTL ≤ Age ≤ max_age: Stale-while-revalidate or force refresh
    - Age > max_age: Always force refresh
    """

    def __init__(self, resolver: Resolver, options: CacheOptions):
        self._resolver = resolver
        self._options = options
        self.name = f"cached({resolver.name})"
        self.metadata: Dict[str, Any] = {}

        # Cache state
        self._cache: Optional[Dict[str, Any]] = None
        self._refresh_task: Optional[asyncio.Task] = None

    async def load(self) -> Dict[str, str]:
        """Load with caching logic."""
        now = time.time()

        # If no cache or cache is expired beyond maxAge, force refresh
        if self._cache is None or (now - self._cache["timestamp"]) > self._options.max_age:
            data = await self._resolver.load()
            self._cache = {"data": data, "timestamp": now}
            self.metadata = {"cached": False}
            return data

        # If cache is within TTL, return cached data (fresh)
        age = now - self._cache["timestamp"]
        if age < self._options.ttl:
            self.metadata = {"cached": True}
            cached_data: dict[str, str] = self._cache["data"]
            return cached_data

        # Cache is stale (between TTL and maxAge)
        # If stale-while-revalidate is enabled, serve stale data while refreshing in background
        if self._options.stale_while_revalidate:
            # Trigger a refresh if one isn't already running, but always serve stale data.
            if self._refresh_task is None or self._refresh_task.done():
                async def background_refresh() -> None:
                    try:
                        data = await self._resolver.load()
                        if self._cache is not None:
                            self._cache["data"] = data
                            self._cache["timestamp"] = time.time()
                    except Exception:
                        # Keep serving stale data if refresh fails.
                        pass
                    finally:
                        self._refresh_task = None

                self._refresh_task = asyncio.create_task(background_refresh())

            self.metadata = {
                "cached": True,
                "stale": True,
                "refresh_in_flight": self._refresh_task is not None
            }
            stale_data: dict[str, str] = self._cache["data"]
            return stale_data

        # Cache is stale and no stale-while-revalidate, force refresh
        data = await self._resolver.load()
        self._cache = {"data": data, "timestamp": now}
        self.metadata = {"cached": False}
        return data


def cached(
    resolver: Resolver,
    options: Optional[CacheOptions] = None
) -> CachedResolver:
    """
    Wrap a resolver with TTL caching.

    Args:
        resolver: The resolver to cache
        options: Cache configuration options

    Returns:
        Cached resolver wrapper

    Example:
        >>> from python_env_resolver import cached, TTL
        >>> from python_env_resolver_aws import aws_secrets
        >>>
        >>> resolver = cached(
        ...     aws_secrets(secret_id="prod/db"),
        ...     CacheOptions(ttl=TTL.minutes5, stale_while_revalidate=True)
        ... )
    """
    if options is None:
        options = CacheOptions()

    return CachedResolver(resolver, options)


def aws_cache(
    ttl: Optional[float] = None,
    max_age: Optional[float] = None,
    stale_while_revalidate: Optional[bool] = None
) -> CacheOptions:
    """
    AWS-optimized cache configuration.

    Args:
        ttl: Cache duration (default: 5 minutes)
        max_age: Maximum age before forcing refresh (default: 1 hour)
        stale_while_revalidate: Enable stale-while-revalidate (default: True)

    Returns:
        CacheOptions configured for AWS

    Example:
        >>> from python_env_resolver import cached, aws_cache
        >>>
        >>> resolver = cached(
        ...     aws_secrets(secret_id="prod/db"),
        ...     aws_cache()  # Uses AWS-optimized defaults
        ... )
    """
    return CacheOptions(
        ttl=ttl if ttl is not None else TTL.minutes5,
        max_age=max_age if max_age is not None else TTL.hour,
        stale_while_revalidate=stale_while_revalidate if stale_while_revalidate is not None else True,
        key="aws-secrets"
    )
