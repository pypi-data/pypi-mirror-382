from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any, Mapping

from .exceptions import CircuitBackendError


class CircuitBackend(ABC):
    """
    Abstract storage backend for the circuit-breaker.
    """

    @abstractmethod
    def initialize(self) -> None:
        """
        Prepare the backend (load scripts, initialize keys). Called once before use.
        """
        raise NotImplementedError

    @abstractmethod
    def record_failure(
        self, service: str, reason: str, timestamp: float | None = None
    ) -> int:
        """
        Record a failure for service and return the new failure count (after cleanup).
        """
        raise NotImplementedError

    @abstractmethod
    def record_success(self, service: str, timestamp: float | None = None) -> None:
        """
        Mark a success/reset for the given service.
        """
        raise NotImplementedError

    @abstractmethod
    def get_failure_count(self, service: str, cutoff: int) -> int:
        """
        Return the number of failures for `service` with timestamp > cutoff.
        """
        raise NotImplementedError

    @abstractmethod
    def get_last_failure(self, service: str) -> Mapping[str, Any] | None:
        """
        Return metadata about last failure for `service` or None.
        Example: {"reason": "SocketError", "ts": 1234567890}
        """
        raise NotImplementedError

    @staticmethod
    def _sanitize_service(
        service: str,
        *,
        allowed: str = r"[A-Za-z0-9_]",
        replacement: str = "_",
        lowercase: bool = True,
    ) -> str:
        collapsed = re.sub(r"\s+", " ", service).strip()

        pattern = rf"[^ {allowed}]"
        cleaned = re.sub(pattern, "", collapsed)

        replaced = cleaned.replace(" ", replacement)

        if lowercase:
            replaced = replaced.lower()

        if len(replaced) > 200:
            raise CircuitBackendError(
                "Service name is too long. Max length is 200 characters."
            )
        return replaced
