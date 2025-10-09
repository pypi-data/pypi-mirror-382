"""
Demo of python-env-resolver features.

Run with: uv run python examples/demo.py
"""

import asyncio
import os
from typing import Literal

from pydantic import BaseModel, HttpUrl

from python_env_resolver import (
    CacheOptions,
    ResolveOptions,
    cached,
    get_audit_log,
    resolve,
    safe_resolve,
)


class Config(BaseModel):
    """Application configuration schema."""

    port: int = 3000
    database_url: HttpUrl
    node_env: Literal["development", "production", "test"] = "development"
    debug: bool = False
    api_key: str | None = None


async def demo_basic():
    """Demo: Basic usage."""
    print("\n=== Demo 1: Basic Usage ===")

    # Set some environment variables
    os.environ["PORT"] = "8080"
    os.environ["DATABASE_URL"] = "https://db.example.com"
    os.environ["NODE_ENV"] = "production"

    config = await resolve(Config)

    print(f"Port: {config.port} (type: {type(config.port).__name__})")
    print(f"Database URL: {config.database_url}")
    print(f"Environment: {config.node_env}")
    print(f"Debug: {config.debug}")


async def demo_safe_resolve():
    """Demo: Safe error handling."""
    print("\n=== Demo 2: Safe Resolve ===")

    # Missing required field
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]

    result = await safe_resolve(Config)

    if result.success:
        print(f"Success! Port: {result.data.port}")
    else:
        print(f"Validation failed: {result.error[:100]}...")


async def demo_caching():
    """Demo: TTL caching."""
    print("\n=== Demo 3: TTL Caching ===")

    call_count = 0

    class MockAwsResolver:
        name = "aws-secrets"
        metadata = {}

        async def load(self):
            nonlocal call_count
            call_count += 1
            print(f"  → Loading from AWS (call #{call_count})")
            await asyncio.sleep(0.1)  # Simulate network delay
            return {
                "PORT": "3000",
                "DATABASE_URL": "https://aws-db.example.com",
            }

    # Wrap with caching
    cached_resolver = cached(
        MockAwsResolver(),
        CacheOptions(ttl=2, stale_while_revalidate=True)
    )

    print("Call 1 (cache miss):")
    data1 = await cached_resolver.load()
    print(f"  ← Got data: {data1['PORT']}")

    print("\nCall 2 (cached, instant):")
    data2 = await cached_resolver.load()
    print(f"  ← Got data: {data2['PORT']} [CACHED]")

    print("\nWaiting 2.5s for TTL to expire...")
    await asyncio.sleep(2.5)

    print("\nCall 3 (stale-while-revalidate):")
    data3 = await cached_resolver.load()
    print(f"  ← Got data instantly: {data3['PORT']} [STALE]")
    print("  → Background refresh triggered")

    await asyncio.sleep(0.2)
    print(f"\nTotal AWS calls: {call_count}")


async def demo_audit():
    """Demo: Audit logging."""
    print("\n=== Demo 4: Audit Logging ===")

    os.environ["PORT"] = "8080"
    os.environ["DATABASE_URL"] = "https://db.example.com"

    _config = await resolve(
        Config,
        options=ResolveOptions(enable_audit=True)
    )

    logs = get_audit_log()
    print(f"\nAudit log ({len(logs)} events):")
    for log in logs:
        if log.key:
            print(f"  - {log.type}: {log.key} from {log.source}")
        else:
            print(f"  - {log.type}")


async def main():
    """Run all demos."""
    print("╔═══════════════════════════════════════════════════════╗")
    print("║       python-env-resolver Demo                        ║")
    print("║  Port of node-env-resolver with Pydantic integration ║")
    print("╚═══════════════════════════════════════════════════════╝")

    await demo_basic()
    await demo_safe_resolve()
    await demo_caching()
    await demo_audit()

    print("\n✅ All demos complete!")


if __name__ == "__main__":
    asyncio.run(main())

