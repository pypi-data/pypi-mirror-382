"""Plugin management for cfdoc."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import lru_cache


# ------------------------------------------------------------------------------
@dataclass(frozen=True)
class Plugin:
    """Container for plugin info."""

    name: str
    description: str
    func: Callable

    def __hash__(self) -> int:
        """Hash on name."""
        return hash(self.name)


_PLUGINS: dict[str, Plugin] = {}


# ------------------------------------------------------------------------------
def plugin(name: str) -> Callable:
    """Register a function as a plugin."""

    def decorate(func: Callable) -> Callable:
        """Register a function as a plugin."""
        _PLUGINS[name] = Plugin(
            name, (func.__doc__ or 'No description available').strip().splitlines()[0], func
        )
        func.name = name
        return func

    return decorate


# ------------------------------------------------------------------------------
@lru_cache
def plugins() -> list[Plugin]:
    """Get a list of plugins ordered by name."""

    return sorted(_PLUGINS.values(), key=lambda p: p.name)
