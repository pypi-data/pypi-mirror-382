# src/arize/_lazy.py
from __future__ import annotations

import logging
import sys
import threading
from importlib import import_module
from typing import TYPE_CHECKING, Any, Dict, Tuple

if TYPE_CHECKING:
    from arize.config import SDKConfiguration

logger = logging.getLogger(__name__)


class LazySubclientsMixin:
    _SUBCLIENTS: Dict[str, Tuple[str, str]] = {}
    _EXTRAS: Dict[str, Tuple[str | None, Tuple[str, ...]]] = {}

    def __init__(self, sdk_config: SDKConfiguration):
        self.sdk_config = sdk_config
        self._lazy_cache: Dict[str, Any] = {}
        self._lazy_lock = threading.Lock()

    def __getattr__(self, name: str) -> Any:
        subs = self._SUBCLIENTS
        if name not in subs:
            raise AttributeError(
                f"{type(self).__name__} has no attribute {name!r}"
            )

        with self._lazy_lock:
            if name in self._lazy_cache:
                return self._lazy_cache[name]

            logger.debug(f"Lazily loading subclient {name!r}")
            module_path, class_name = subs[name]
            extra_key, required = self._EXTRAS.get(name, (None, ()))
            require(extra_key, required)

            module = _dynamic_import(module_path)
            klass = getattr(module, class_name)

            # Pass sdk_config if the child accepts it; otherwise construct bare.
            try:
                instance = klass(self.sdk_config)
            except TypeError:
                instance = klass()

            self._lazy_cache[name] = instance
            return instance

    def __dir__(self):
        return sorted({*super().__dir__(), *self._SUBCLIENTS.keys()})


class OptionalDependencyError(ImportError): ...


def require(
    extra_key: str | None,
    required: Tuple[str, ...],
    pkgname="arize",
):
    if not required:
        return
    missing = []
    for p in required:
        try:
            import_module(p)
        except Exception:
            missing.append(p)
    if missing:
        raise OptionalDependencyError(
            f"Missing optional dependencies: {', '.join(missing)}. "
            f"Install via: pip install {pkgname}[{extra_key}]"
        )


def _dynamic_import(modname: str, retries: int = 2):
    for i in range(retries):
        try:
            return import_module(modname)
        except (ModuleNotFoundError, ImportError, KeyError):
            sys.modules.pop(modname, None)
            if i + 1 == retries:
                raise
