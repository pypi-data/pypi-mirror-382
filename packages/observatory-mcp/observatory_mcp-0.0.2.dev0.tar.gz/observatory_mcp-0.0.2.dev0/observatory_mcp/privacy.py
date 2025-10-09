"""Privacy and PII detection/masking utilities."""

import re
from typing import Any

from .config import PrivacyConfig
from .utils import hash_string


class PrivacyManager:
    """Manages PII detection and data masking."""

    # PII detection patterns
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b")
    SSN_PATTERN = re.compile(r"\b\d{3}-\d{2}-\d{4}\b")
    CREDIT_CARD_PATTERN = re.compile(r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b")
    PHONE_PATTERN = re.compile(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b")
    IP_ADDRESS_PATTERN = re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b")
    API_KEY_PATTERN = re.compile(r"\b[A-Za-z0-9_-]{20,}\b")  # Generic long alphanumeric strings

    def __init__(self, config: PrivacyConfig):
        """Initialize privacy manager.

        Args:
            config: Privacy configuration
        """
        self.config = config
        self._sensitive_field_patterns = [
            re.compile(pattern, re.IGNORECASE) for pattern in config.sensitive_field_masks
        ]

    def detect_pii(self, data: Any) -> set[str]:
        """Detect PII in data.

        Args:
            data: Data to scan for PII

        Returns:
            Set of PII types found
        """
        if not self.config.enable_pii_detection:
            return set()

        pii_types = set()
        text = self._extract_text(data)

        if self.EMAIL_PATTERN.search(text):
            pii_types.add("email")
        if self.SSN_PATTERN.search(text):
            pii_types.add("ssn")
        if self.CREDIT_CARD_PATTERN.search(text):
            pii_types.add("credit_card")
        if self.PHONE_PATTERN.search(text):
            pii_types.add("phone")
        if self.IP_ADDRESS_PATTERN.search(text):
            pii_types.add("ip_address")

        return pii_types

    def mask_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Mask sensitive data in dictionary.

        Args:
            data: Data to mask

        Returns:
            Masked data dictionary
        """
        if not isinstance(data, dict):
            return data

        masked = {}
        for key, value in data.items():
            if self._is_sensitive_field(key):
                masked[key] = self._mask_value(value)
            elif isinstance(value, dict):
                masked[key] = self.mask_data(value)  # type: ignore[assignment]
            elif isinstance(value, list):
                masked[key] = [  # type: ignore[assignment]
                    self.mask_data(item) if isinstance(item, dict) else item for item in value
                ]
            else:
                # Check if value contains PII
                if isinstance(value, str) and self._contains_pii(value):
                    masked[key] = self._redact_pii(value)
                else:
                    masked[key] = value

        return masked

    def hash_identifier(self, value: str) -> str:
        """Hash an identifier value.

        Args:
            value: Value to hash

        Returns:
            Hashed value
        """
        if not self.config.hash_identifiers:
            return value
        return hash_string(value)

    def sanitize_error_message(self, message: str) -> str:
        """Sanitize error message to remove PII.

        Args:
            message: Error message

        Returns:
            Sanitized message
        """
        if not self.config.redact_errors:
            return message

        sanitized = message
        sanitized = self.EMAIL_PATTERN.sub("[EMAIL]", sanitized)
        sanitized = self.SSN_PATTERN.sub("[SSN]", sanitized)
        sanitized = self.CREDIT_CARD_PATTERN.sub("[CREDIT_CARD]", sanitized)
        sanitized = self.PHONE_PATTERN.sub("[PHONE]", sanitized)
        sanitized = self.IP_ADDRESS_PATTERN.sub("[IP_ADDRESS]", sanitized)

        return sanitized

    def _is_sensitive_field(self, field_name: str) -> bool:
        """Check if field name matches sensitive patterns.

        Args:
            field_name: Field name to check

        Returns:
            True if field is sensitive
        """
        return any(pattern.search(field_name) for pattern in self._sensitive_field_patterns)

    def _mask_value(self, value: Any) -> str:
        """Mask a value.

        Args:
            value: Value to mask

        Returns:
            Masked value
        """
        if value is None:
            return "[MASKED:null]"
        if isinstance(value, (int, float)):
            return "[MASKED:number]"
        if isinstance(value, bool):
            return "[MASKED:boolean]"
        if isinstance(value, str):
            if len(value) > 4:
                # Show last 4 characters for partial identification
                return f"[MASKED]...{value[-4:]}"
            return "[MASKED]"
        return "[MASKED:complex]"

    def _contains_pii(self, text: str) -> bool:
        """Check if text contains PII.

        Args:
            text: Text to check

        Returns:
            True if PII detected
        """
        return bool(
            self.EMAIL_PATTERN.search(text)
            or self.SSN_PATTERN.search(text)
            or self.CREDIT_CARD_PATTERN.search(text)
        )

    def _redact_pii(self, text: str) -> str:
        """Redact PII from text.

        Args:
            text: Text to redact

        Returns:
            Redacted text
        """
        redacted = text
        redacted = self.EMAIL_PATTERN.sub("[EMAIL]", redacted)
        redacted = self.SSN_PATTERN.sub("[SSN]", redacted)
        redacted = self.CREDIT_CARD_PATTERN.sub("[CREDIT_CARD]", redacted)
        return redacted

    def _extract_text(self, data: Any) -> str:
        """Extract text from data for PII scanning.

        Args:
            data: Data to extract text from

        Returns:
            Concatenated text
        """
        if isinstance(data, str):
            return data
        elif isinstance(data, dict):
            return " ".join(self._extract_text(v) for v in data.values())
        elif isinstance(data, list):
            return " ".join(self._extract_text(item) for item in data)
        else:
            return str(data)
