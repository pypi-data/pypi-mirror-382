"""
python-env-resolver: Type-safe environment variable handling for Python

Port of node-env-resolver with Pydantic integration.
"""

from .audit import (
    clear_audit_log,
    get_audit_log,
    log_audit_event,
)
from .resolver import (
    resolve,
    resolve_sync,
    safe_resolve,
    safe_resolve_sync,
)
from .resolvers import (
    DotenvResolver,
    ProcessEnvResolver,
    dotenv,
    process_env,
)
from .types import (
    AuditEvent,
    CacheOptions,
    PolicyOptions,
    Provenance,
    ResolveOptions,
    Resolver,
)
from .utils import (
    TTL,
    CachedResolver,
    aws_cache,
    cached,
)
from .validators import (
    validate_boolean,
    validate_email,
    validate_http,
    validate_https,
    validate_integer,
    validate_json,
    validate_mongodb,
    validate_mysql,
    validate_number,
    validate_port,
    validate_postgres,
    validate_redis,
    validate_url,
)

__all__ = [
    # Main API
    "resolve",
    "safe_resolve",
    "resolve_sync",
    "safe_resolve_sync",
    # Types
    "Resolver",
    "PolicyOptions",
    "Provenance",
    "AuditEvent",
    "ResolveOptions",
    "CacheOptions",
    # Resolvers
    "ProcessEnvResolver",
    "DotenvResolver",
    "process_env",
    "dotenv",
    # Caching
    "CachedResolver",
    "cached",
    "TTL",
    "aws_cache",
    # Validators
    "validate_url",
    "validate_http",
    "validate_https",
    "validate_email",
    "validate_port",
    "validate_postgres",
    "validate_mysql",
    "validate_mongodb",
    "validate_redis",
    "validate_json",
    "validate_boolean",
    "validate_number",
    "validate_integer",
    # Audit
    "get_audit_log",
    "clear_audit_log",
    "log_audit_event",
]

__version__ = "0.1.0"
