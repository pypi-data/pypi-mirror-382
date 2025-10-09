"""
Basic tests for python-env-resolver.

Tests core functionality: resolvers, validation, caching, policies.
"""

import asyncio
import os
from typing import Literal, Optional

import pytest
from pydantic import BaseModel, HttpUrl

from python_env_resolver import (
    TTL,
    CacheOptions,
    PolicyOptions,
    ResolveOptions,
    aws_cache,
    cached,
    clear_audit_log,
    dotenv,
    get_audit_log,
    process_env,
    resolve,
    resolve_sync,
    safe_resolve,
    safe_resolve_sync,
)


class SimpleConfig(BaseModel):
    """Simple config for testing."""
    port: int = 3000
    debug: bool = False
    database_url: HttpUrl


class EnumConfig(BaseModel):
    """Config with enum for testing."""
    node_env: Literal["development", "production", "test"]
    log_level: Literal["debug", "info", "warn", "error"] = "info"


class OptionalConfig(BaseModel):
    """Config with optional fields."""
    api_key: Optional[str] = None
    redis_url: Optional[HttpUrl] = None
    port: int = 3000


@pytest.fixture(autouse=True)
def clean_env():
    """Clean environment before each test."""
    original_env = dict(os.environ)
    clear_audit_log()

    yield

    # Restore
    os.environ.clear()
    os.environ.update(original_env)
    clear_audit_log()


@pytest.mark.asyncio
async def test_basic_resolve():
    """Test basic resolution from process.env."""
    os.environ["PORT"] = "8080"
    os.environ["DEBUG"] = "true"
    os.environ["DATABASE_URL"] = "https://db.example.com"

    config = await resolve(SimpleConfig)

    assert config.port == 8080
    assert config.debug is True
    assert str(config.database_url) == "https://db.example.com/"


@pytest.mark.asyncio
async def test_default_values():
    """Test that default values are used when env var is missing."""
    os.environ["DATABASE_URL"] = "https://db.example.com"
    # PORT and DEBUG not set - should use defaults

    config = await resolve(SimpleConfig)

    assert config.port == 3000  # Default
    assert config.debug is False  # Default
    assert str(config.database_url) == "https://db.example.com/"


@pytest.mark.asyncio
async def test_enum_validation():
    """Test enum validation."""
    os.environ["NODE_ENV"] = "production"
    os.environ["LOG_LEVEL"] = "debug"

    config = await resolve(EnumConfig)

    assert config.node_env == "production"
    assert config.log_level == "debug"


@pytest.mark.asyncio
async def test_enum_validation_failure():
    """Test enum validation fails for invalid values."""
    os.environ["NODE_ENV"] = "staging"  # Invalid

    with pytest.raises(ValueError, match="validation failed"):
        await resolve(EnumConfig)


@pytest.mark.asyncio
async def test_optional_values():
    """Test optional fields."""
    os.environ["PORT"] = "3000"
    # api_key and redis_url not set - should be None

    config = await resolve(OptionalConfig)

    assert config.port == 3000
    assert config.api_key is None
    assert config.redis_url is None


@pytest.mark.asyncio
async def test_safe_resolve_success():
    """Test safe_resolve returns success result."""
    os.environ["PORT"] = "8080"
    os.environ["DATABASE_URL"] = "https://db.example.com"

    result = await safe_resolve(SimpleConfig)

    assert result.success is True
    assert result.data.port == 8080
    assert result.error is None


@pytest.mark.asyncio
async def test_safe_resolve_failure():
    """Test safe_resolve returns error result."""
    # Missing required DATABASE_URL

    result = await safe_resolve(SimpleConfig)

    assert result.success is False
    assert result.data is None
    assert "validation failed" in result.error.lower()


def test_resolve_sync_basic():
    """resolve_sync should return validated config without awaiting."""
    os.environ["PORT"] = "9090"
    os.environ["DATABASE_URL"] = "https://db.example.com"

    config = resolve_sync(SimpleConfig)

    assert config.port == 9090
    assert str(config.database_url) == "https://db.example.com/"


@pytest.mark.asyncio
async def test_resolve_sync_inside_event_loop():
    """resolve_sync should work even when an event loop is already running."""
    os.environ["PORT"] = "7070"
    os.environ["DATABASE_URL"] = "https://db.example.com"

    config = resolve_sync(SimpleConfig)

    assert config.port == 7070


def test_safe_resolve_sync_failure():
    """safe_resolve_sync should surface validation errors without raising."""
    result = safe_resolve_sync(SimpleConfig)

    assert result.success is False
    assert result.data is None
    assert "validation failed" in result.error.lower()


@pytest.mark.asyncio
async def test_caching():
    """Test that caching works."""
    call_count = 0

    class CountingResolver:
        name = "counter"
        metadata = {}

        async def load(self):
            nonlocal call_count
            call_count += 1
            return {"PORT": "3000"}

    cached_resolver = cached(CountingResolver(), CacheOptions(ttl=1.0))

    # First call - cache miss
    data1 = await cached_resolver.load()
    assert data1 == {"PORT": "3000"}
    assert call_count == 1

    # Second call - cache hit
    data2 = await cached_resolver.load()
    assert data2 == {"PORT": "3000"}
    assert call_count == 1  # Not called again

    # Wait for TTL to expire
    await asyncio.sleep(1.1)

    # Third call - cache expired
    data3 = await cached_resolver.load()
    assert data3 == {"PORT": "3000"}
    assert call_count == 2  # Called again


@pytest.mark.asyncio
async def test_stale_while_revalidate():
    """Test stale-while-revalidate caching."""
    call_count = 0

    class CountingResolver:
        name = "counter"
        metadata = {}

        async def load(self):
            nonlocal call_count
            call_count += 1
            return {"PORT": f"{3000 + call_count}"}

    cached_resolver = cached(
        CountingResolver(),
        CacheOptions(ttl=0.05, max_age=1.0, stale_while_revalidate=True)
    )

    # First call
    data1 = await cached_resolver.load()
    assert data1 == {"PORT": "3001"}
    assert call_count == 1

    # Wait for TTL to expire
    await asyncio.sleep(0.06)

    # Second call - should return stale data immediately
    data2 = await cached_resolver.load()
    assert data2 == {"PORT": "3001"}  # Stale data
    assert cached_resolver.metadata.get("stale") is True
    assert call_count == 1  # Refresh still running in background

    # Wait for background refresh
    await asyncio.sleep(0.05)

    # Eventually refresh completes
    assert call_count == 2

    # Third call - should return fresh data
    data3 = await cached_resolver.load()
    assert data3 == {"PORT": "3002"}  # Fresh from background refresh


@pytest.mark.asyncio
async def test_audit_logging():
    """Test audit logging functionality."""
    os.environ["PORT"] = "3000"
    os.environ["DATABASE_URL"] = "https://db.example.com"

    clear_audit_log()

    await resolve(
        SimpleConfig,
        options=ResolveOptions(enable_audit=True)
    )

    logs = get_audit_log()

    # Should have env_loaded events + validation_success
    assert len(logs) >= 2

    env_loaded = [log for log in logs if log.type == "env_loaded"]
    assert len(env_loaded) >= 1

    validation_success = [log for log in logs if log.type == "validation_success"]
    assert len(validation_success) == 1


@pytest.mark.asyncio
async def test_policy_allow_dotenv_in_production(tmp_path):
    """Test allowDotenvInProduction policy."""
    # Create a temporary .env file
    env_file = tmp_path / ".env"
    env_file.write_text("PORT=8080\nDATABASE_URL=https://db.example.com\nDEBUG=false\n")

    # Simulate production
    os.environ["PYTHON_ENV"] = "production"

    # Should fail without policy
    with pytest.raises(ValueError, match="cannot be sourced from .env"):
        await resolve(
            SimpleConfig,
            resolvers=[dotenv(str(env_file))],
            options=ResolveOptions(
                policies=PolicyOptions(allow_dotenv_in_production=None)
            )
        )


@pytest.mark.asyncio
async def test_policy_enforce_allowed_sources():
    """Test enforceAllowedSources policy."""

    class MockAwsResolver:
        name = "aws-secrets"
        metadata = {}

        async def load(self):
            return {
                "PORT": "3000",
                "DATABASE_URL": "https://db.example.com"
            }

    os.environ["PORT"] = "8080"  # From process.env

    # PORT comes from process.env, but policy requires aws-secrets
    with pytest.raises(ValueError, match="must be sourced from"):
        await resolve(
            SimpleConfig,
            resolvers=[process_env(), MockAwsResolver()],
            options=ResolveOptions(
                priority="first",  # process.env wins (wrong source)
                policies=PolicyOptions(
                    enforce_allowed_sources={
                        "PORT": ["aws-secrets"],  # PORT must come from AWS
                    }
                )
            )
        )


@pytest.mark.asyncio
async def test_ttl_constants():
    """Test TTL constants."""
    assert TTL.short == 30
    assert TTL.minute == 60
    assert TTL.minutes5 == 300
    assert TTL.minutes15 == 900
    assert TTL.hour == 3600
    assert TTL.hours6 == 21600
    assert TTL.day == 86400


@pytest.mark.asyncio
async def test_aws_cache_helper():
    """Test aws_cache helper function."""
    cache_opts = aws_cache()

    assert cache_opts.ttl == TTL.minutes5
    assert cache_opts.max_age == TTL.hour
    assert cache_opts.stale_while_revalidate is True
    assert cache_opts.key == "aws-secrets"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
