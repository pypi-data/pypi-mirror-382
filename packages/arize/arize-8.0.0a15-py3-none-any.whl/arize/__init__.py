# src/arize/__init__.py
import logging

from arize.client import ArizeClient
from arize.config import SDKConfiguration

# Attach a NullHandler by default in the top-level package
# so that if no configuration is installed, nothing explodes.
logging.getLogger("arize").addHandler(logging.NullHandler())

# Opt-in env-based logging
try:
    from .logging import auto_configure_from_env

    auto_configure_from_env()
except Exception:
    # Never let logging config crash imports
    pass

__all__ = ["ArizeClient", "SDKConfiguration"]
