"""grayven package entry file."""

__all__ = ["__version__", "get_cache_root"]
__version__ = "0.4.0"

import os
from pathlib import Path


def get_cache_root() -> Path:
    """Create and return the path to the cache for Grayven, supports XDG_CACHE_HOME env.

    Returns:
        The path to the Grayven cache folder.
    """
    cache_home = os.getenv("XDG_CACHE_HOME", default=str(Path.home() / ".cache"))
    folder = Path(cache_home).resolve() / "grayven"
    folder.mkdir(parents=True, exist_ok=True)
    return folder
