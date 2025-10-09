"""
Core types for python-env-resolver.

Defines the core abstractions: Resolver protocol, policy options, and audit events.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Optional, Protocol, Union


class Resolver(Protocol):
    """
    Protocol for environment variable resolvers.

    A resolver loads environment variables from a specific source
    (e.g., os.environ, .env file, AWS Secrets Manager, etc.).
    """

    name: str
    metadata: Dict[str, Any]

    async def load(self) -> Dict[str, str]:
        """Load environment variables from this source."""
        ...


@dataclass
class PolicyOptions:
    """
    Security policies to control where environment variables can be loaded from.

    Attributes:
        allow_dotenv_in_production: Control loading from .env files in production.
            - None (default): .env files completely blocked in production
            - True: Allow all vars from .env in production (NOT recommended)
            - List[str]: Allow only specific vars from .env in production

        enforce_allowed_sources: Restrict variables to specific resolvers.
            Example: {"DATABASE_PASSWORD": ["aws-secrets"]}
    """

    allow_dotenv_in_production: Optional[Union[bool, List[str]]] = None
    enforce_allowed_sources: Optional[Dict[str, List[str]]] = None


@dataclass
class Provenance:
    """
    Tracks where an environment variable was loaded from.

    Attributes:
        source: Name of the resolver that provided this variable
        timestamp: When the variable was loaded (seconds since epoch)
        cached: Whether this value came from cache
    """

    source: str
    timestamp: float
    cached: Optional[bool] = None


AuditEventType = Literal[
    "validation_success",
    "validation_failure",
    "policy_violation",
    "env_loaded",
    "resolver_error",
]


@dataclass
class AuditEvent:
    """
    An event in the audit log.

    Attributes:
        type: Type of audit event
        timestamp: When the event occurred (seconds since epoch)
        key: Environment variable key (if applicable)
        source: Resolver name (if applicable)
        error: Error message (if applicable)
        metadata: Additional event metadata
    """

    type: AuditEventType
    timestamp: float
    key: Optional[str] = None
    source: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class CacheOptions:
    """
    Options for caching resolver results.

    Attributes:
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        max_age: Maximum age in seconds before forcing refresh (default: 3600 = 1 hour)
        stale_while_revalidate: Serve stale data while refreshing in background
        key: Custom cache key for debugging
    """

    ttl: float = 300  # 5 minutes
    max_age: float = 3600  # 1 hour
    stale_while_revalidate: bool = False
    key: Optional[str] = None


@dataclass
class ResolveOptions:
    """
    Options for environment resolution.

    Attributes:
        interpolate: Enable variable interpolation using ${VAR_NAME} syntax
        strict: Fail-fast if any resolver fails (vs graceful degradation)
        priority: Merge strategy when multiple resolvers provide same variable
        policies: Security policies to enforce
        enable_audit: Enable audit logging
    """

    interpolate: bool = True
    strict: bool = True
    priority: Literal["first", "last"] = "last"
    policies: Optional[PolicyOptions] = None
    enable_audit: Optional[bool] = None  # None = auto (true in production)

