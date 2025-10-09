"""
Built-in resolvers for environment variable resolution.

Provides resolvers for common sources: os.environ and .env files.
"""

import os
from pathlib import Path
from typing import Dict

from dotenv import dotenv_values


class ProcessEnvResolver:
    """
    Resolver that loads from os.environ (process environment variables).

    This is the default resolver and works in all environments.
    """

    name = "process.env"
    metadata: Dict = {}

    async def load(self) -> Dict[str, str]:
        """Load from os.environ."""
        return {k: v for k, v in os.environ.items() if v is not None}


class DotenvResolver:
    """
    Resolver that loads from .env files.

    Args:
        path: Path to .env file (default: ".env")
    """

    def __init__(self, path: str = ".env"):
        self.path = path
        self.name = f"dotenv({path})"
        self.metadata: Dict = {}

    async def load(self) -> Dict[str, str]:
        """Load from .env file."""
        env_path = Path(self.path)
        if not env_path.exists():
            return {}

        values = dotenv_values(self.path)
        # Filter out None values
        return {k: v for k, v in values.items() if v is not None}


def process_env() -> ProcessEnvResolver:
    """
    Create a resolver for os.environ.

    Returns:
        ProcessEnvResolver instance

    Example:
        >>> from python_env_resolver import resolve, process_env
        >>> config = await resolve.with_sources(
        ...     [process_env(), {"PORT": (int, 3000)}]
        ... )
    """
    return ProcessEnvResolver()


def dotenv(path: str = ".env") -> DotenvResolver:
    """
    Create a resolver for .env files.

    Args:
        path: Path to .env file (default: ".env")

    Returns:
        DotenvResolver instance

    Example:
        >>> from python_env_resolver import resolve, dotenv
        >>> config = await resolve.with_sources(
        ...     [dotenv(".env.local"), {"DATABASE_URL": str}]
        ... )
    """
    return DotenvResolver(path)

