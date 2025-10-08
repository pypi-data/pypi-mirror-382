"""
Compatibility helpers for legacy module names.
"""

import importlib
import logging
import sys
from types import ModuleType
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def _import_optional_module(name: str) -> Optional[ModuleType]:
    """Attempt to import a module, returning None when it is missing."""
    try:
        return importlib.import_module(name)
    except ModuleNotFoundError:
        return None


def ensure_gtasks_module() -> None:
    """
    Ensure the Google Tasks package is available as `gtasks`.

    Historical builds published the package as `gTasks`, which breaks imports on
    case-sensitive filesystems. This helper registers a compatibility alias so the
    rest of the codebase can consistently rely on `gtasks`.
    """
    if 'gtasks' in sys.modules:
        # Already loaded or previously aliased; nothing to do.
        return

    # Fast path: module is importable with the expected name.
    if _import_optional_module('gtasks.tasks_tools') is not None:
        return

    legacy_pkg, legacy_module = _load_legacy_gtasks()
    if legacy_pkg is None or legacy_module is None:
        # Neither modern nor legacy modules are available — let the original
        # ModuleNotFoundError bubble up to caller for clearer diagnostics.
        importlib.import_module('gtasks.tasks_tools')
        return

    sys.modules['gtasks'] = legacy_pkg
    sys.modules['gtasks.tasks_tools'] = legacy_module
    logger.warning(
        "Registered legacy Google Tasks module 'gTasks' under expected package name 'gtasks'. "
        "Please rebuild the package to ship the lowercase module."
    )


def _load_legacy_gtasks() -> Tuple[Optional[ModuleType], Optional[ModuleType]]:
    """Attempt to load the legacy `gTasks` package and tools module."""
    legacy_pkg = _import_optional_module('gTasks')
    if legacy_pkg is None:
        return None, None

    legacy_module = _import_optional_module('gTasks.tasks_tools')
    if legacy_module is None:
        return None, None

    return legacy_pkg, legacy_module

