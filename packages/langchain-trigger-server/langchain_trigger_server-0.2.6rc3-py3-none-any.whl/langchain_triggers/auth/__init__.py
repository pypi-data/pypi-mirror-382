"""Authentication utilities for trigger webhooks."""

from .slack_hmac import (
    verify_slack_signature,
    get_slack_signing_secret,
    extract_slack_headers,
    SlackSignatureVerificationError,
)

__all__ = [
    "verify_slack_signature",
    "get_slack_signing_secret",
    "extract_slack_headers",
    "SlackSignatureVerificationError",
]

