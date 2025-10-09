"""
Audit logging for environment variable resolution.

Tracks where environment variables are loaded from for security and compliance.
"""

from typing import List

from .types import AuditEvent

# Global audit log with max size to prevent memory leaks
_audit_log: List[AuditEvent] = []
MAX_AUDIT_EVENTS = 1000


def log_audit_event(event: AuditEvent) -> None:
    """
    Log an audit event.

    Args:
        event: The audit event to log
    """
    _audit_log.append(event)

    # Keep only last 1000 events to prevent memory leaks
    if len(_audit_log) > MAX_AUDIT_EVENTS:
        _audit_log.pop(0)


def get_audit_log() -> List[AuditEvent]:
    """
    Get a copy of the current audit log.

    Returns:
        List of audit events
    """
    return _audit_log.copy()


def clear_audit_log() -> None:
    """Clear the audit log."""
    _audit_log.clear()

