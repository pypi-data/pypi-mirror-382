from typing import Any


class CircuitError(Exception):
    """Base for circuit errors."""


class CircuitOpenError(CircuitError):
    """Raised when an operation is attempted while the circuit is open."""


class CircuitBackendError(CircuitError):
    """Raised when the backend fails to operate."""


class ReturnValuePolicyError(CircuitOpenError):
    """Raised when the return value policy is invalid."""

    def __init__(self, message: str, retval: Any, retval_policy: Any = None):
        self.message: str = message
        self.retval: Any = retval
        self.retval_policy = retval_policy
        super().__init__(message, retval, retval_policy)
