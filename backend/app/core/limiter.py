"""Shared rate limiter. Limits are read from settings on every request."""

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# Keyed by client IP. Storage is in-memory (per process), which suits a single instance.
limiter = Limiter(key_func=get_remote_address, enabled=settings.rate_limit_enabled)
