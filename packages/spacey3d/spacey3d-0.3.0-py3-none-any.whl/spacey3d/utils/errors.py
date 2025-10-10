from typing import Any, Optional


class APIError(Exception):
    """Raised when the local backend returns an error envelope or HTTP error."""

    def __init__(self, message: str, details: Optional[Any] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.details = details
        self.status_code = status_code

    def __str__(self) -> str:
        base = super().__str__()
        # If backend provided structured details, surface them for DX without needing imports
        if self.details is None:
            return base
        try:
            # Prefer concise message for common shapes
            if isinstance(self.details, dict) and "message_validate" in self.details:
                mv = self.details["message_validate"]
                if isinstance(mv, (list, tuple)) and len(mv) >= 1:
                    # e.g., ["native_platform must be one of ...", "native_platform"]
                    return f"{base}: {mv[0]}"
            return f"{base}: {self.details}"
        except Exception:
            return base



