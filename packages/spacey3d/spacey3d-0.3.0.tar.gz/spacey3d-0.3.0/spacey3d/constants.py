"""Shared SDK constants."""

# Local backend is fixed and stable; override via env var only for development.
BASE_URL: str = "http://127.0.0.1:9765"

# (connect_timeout_s, read_timeout_s)
CONNECT_TIMEOUT_S: int = 10
READ_TIMEOUT_S: int = 60 * 60 * 6


