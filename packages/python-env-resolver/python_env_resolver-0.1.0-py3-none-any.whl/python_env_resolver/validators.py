"""
Built-in validators for common environment variable types.

Provides validators for URLs, emails, database connection strings, etc.
"""

import json
import re
from typing import Any
from urllib.parse import urlparse

from pydantic import EmailStr, ValidationError


def validate_url(value: str) -> str:
    """
    Validate generic URL with protocol whitelist.

    Allowed protocols: http, https, ws, wss, ftp, ftps, file,
                       postgres, postgresql, mysql, mongodb, redis, rediss
    """
    try:
        parsed = urlparse(value)
        allowed_protocols = [
            'http', 'https', 'ws', 'wss', 'ftp', 'ftps', 'file',
            'postgres', 'postgresql', 'mysql', 'mongodb', 'redis', 'rediss'
        ]
        if parsed.scheme not in allowed_protocols:
            raise ValueError(f"URL protocol '{parsed.scheme}:' is not allowed")
        return value
    except Exception as e:
        raise ValueError(f"Invalid URL: {e}")


def validate_http(value: str) -> str:
    """Validate HTTP or HTTPS URL."""
    if not re.match(r'^https?://.+', value):
        raise ValueError("Invalid HTTP URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid HTTP URL")


def validate_https(value: str) -> str:
    """Validate HTTPS URL only (strict)."""
    if not re.match(r'^https://.+', value):
        raise ValueError("Invalid HTTPS URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid HTTPS URL")


def validate_email(value: str) -> str:
    """Validate email address using Pydantic's EmailStr."""
    try:
        # Use Pydantic's email validator
        from pydantic import TypeAdapter
        adapter = TypeAdapter(EmailStr)
        adapter.validate_python(value)
        return value
    except ValidationError:
        raise ValueError("Invalid email address")


def validate_port(value: str) -> int:
    """Validate port number (1-65535)."""
    try:
        port = int(value)
        if port < 1 or port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        return port
    except ValueError as e:
        if "invalid literal" in str(e):
            raise ValueError("Invalid port number")
        raise


def validate_postgres(value: str) -> str:
    """Validate PostgreSQL connection string."""
    if not re.match(r'^postgres(ql)?://.+', value):
        raise ValueError("Invalid PostgreSQL URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid PostgreSQL URL")


def validate_mysql(value: str) -> str:
    """Validate MySQL connection string."""
    if not re.match(r'^mysql://.+', value):
        raise ValueError("Invalid MySQL URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid MySQL URL")


def validate_mongodb(value: str) -> str:
    """
    Validate MongoDB connection string.

    Supports mongodb:// and mongodb+srv:// with replica sets.
    """
    if not re.match(r'^mongodb(\+srv)?://.+', value):
        raise ValueError("Invalid MongoDB URL")

    # MongoDB supports multiple hosts (replica sets), so basic pattern match
    mongo_pattern = r'^mongodb(\+srv)?://([^@]+@)?[^/]+(/[^?]*)?(\\?.*)?$'
    if not re.match(mongo_pattern, value):
        raise ValueError("Invalid MongoDB URL")

    return value


def validate_redis(value: str) -> str:
    """
    Validate Redis connection string.

    Supports redis:// and rediss:// (TLS).
    """
    if not re.match(r'^rediss?://.+', value):
        raise ValueError("Invalid Redis URL")
    try:
        urlparse(value)
        return value
    except Exception:
        raise ValueError("Invalid Redis URL")


def validate_json(value: str) -> Any:
    """
    Validate and parse JSON string.

    Returns:
        Parsed JSON value
    """
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON")


def validate_boolean(value: str) -> bool:
    """
    Validate and coerce boolean from string.

    Accepts: true/false, 1/0, yes/no, on/off (case-insensitive)
    Empty string is treated as False.
    """
    lower = value.lower().strip()
    if lower in ['true', '1', 'yes', 'on']:
        return True
    elif lower in ['false', '0', 'no', 'off', '']:
        return False
    else:
        raise ValueError("Invalid boolean value")


def validate_number(value: str) -> float:
    """Validate and coerce number from string."""
    try:
        return float(value)
    except ValueError:
        raise ValueError("Invalid number")


def validate_integer(value: str) -> int:
    """Validate and coerce integer from string."""
    try:
        return int(value)
    except ValueError:
        raise ValueError("Invalid integer")

