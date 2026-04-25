"""
Echorouk Editorial OS — Structured Logging
========================================
Centralized structured logging with structlog.
Includes log redaction for sensitive data (API keys, tokens, auth headers).
"""

import logging
import re
from typing import Any

import structlog

# Sensitive patterns to redact from logs
SENSITIVE_PATTERNS = [
    # API Keys and Tokens
    (r'(?i)(api[_-]?key|apikey)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?', r'\1=[REDACTED]'),
    (r'(?i)(secret[_-]?key|secretkey)\s*[=:]\s*["\']?([a-zA-Z0-9_\-]{16,})["\']?', r'\1=[REDACTED]'),
    # Authorization Headers
    (r'(?i)(authorization)\s*[=:]\s*["\']?(bearer\s+[a-zA-Z0-9_\-\.]+)["\']?', r'\1=[REDACTED]'),
    (r'(?i)(authorization)\s*[=:]\s*["\']?([a-zA-Z0-9_\-\.]+)["\']?', r'\1=[REDACTED]'),
    # Bearer tokens standalone
    (r'(?i)bearer\s+([a-zA-Z0-9_\-\.]{20,})', 'bearer=[REDACTED]'),
    # Cookies
    (r'(?i)(cookie)\s*[=:]\s*["\']?([^"\';]{20,})["\']?', r'\1=[REDACTED]'),
    # Passwords in URLs or configs
    (r'(?i)(password|passwd|pwd)\s*[=:]\s*["\']?([^"\'\s]{4,})["\']?', r'\1=[REDACTED]'),
]

# Headers to always redact
REDACT_HEADERS = {
    'authorization',
    'cookie',
    'set-cookie',
    'x-api-key',
    'x-auth-token',
    'x-access-token',
}


def sanitize_log_payload(payload: Any) -> Any:
    """Recursively sanitize a payload to remove sensitive data."""
    if isinstance(payload, str):
        result = payload
        for pattern, replacement in SENSITIVE_PATTERNS:
            result = re.sub(pattern, replacement, result)
        return result
    elif isinstance(payload, dict):
        return {k: sanitize_log_payload(v) for k, v in payload.items()}
    elif isinstance(payload, (list, tuple)):
        return type(payload)(sanitize_log_payload(item) for item in payload)
    else:
        return payload


def redact_headers(headers: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive headers from a headers dict."""
    if not headers:
        return {}
    result = {}
    for key, value in headers.items():
        key_lower = key.lower()
        if key_lower in REDACT_HEADERS:
            result[key] = '[REDACTED]'
        else:
            result[key] = sanitize_log_payload(value)
    return result


def redact_sensitive_data(
    logger: Any, method_name: str, event_dict: dict[str, Any]
) -> dict[str, Any]:
    """Structlog processor that redacts sensitive data from log events."""
    # Redact any 'headers' field
    if 'headers' in event_dict:
        event_dict['headers'] = redact_headers(event_dict['headers'])
    
    # Sanitize all string fields
    for key, value in event_dict.items():
        if isinstance(value, str):
            event_dict[key] = sanitize_log_payload(value)
    
    return event_dict


def setup_logging(debug: bool = False):
    """Configure structured logging for the application."""

    log_level = logging.DEBUG if debug else logging.INFO

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            redact_sensitive_data,  # Redact sensitive data before rendering
            structlog.dev.ConsoleRenderer() if debug else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    # Suppress verbose HTTP client logging that might leak headers
    logging.getLogger("httpx._client").setLevel(logging.ERROR)


def get_logger(name: str = None):
    """Get a structured logger instance."""
    return structlog.get_logger(name)
