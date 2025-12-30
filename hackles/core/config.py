"""Global configuration and state management for Hackles"""
import threading
from typing import Dict, Set


class Config:
    """Thread-safe singleton configuration class for global state.

    Uses an RLock to protect mutable state access. While hackles is primarily
    a single-threaded CLI tool, thread safety prevents issues if the code
    is ever used in a threaded context.
    """

    def __init__(self):
        self._lock = threading.RLock()
        self._owned_cache: Dict[str, bool] = {}
        self._quiet_mode: bool = False
        self._show_abuse: bool = False
        self._debug_mode: bool = False
        self._no_color: bool = False
        self._output_format: str = 'table'  # table, json, csv, html
        self._severity_filter: Set[str] = set()  # Empty = all severities
        self._show_progress: bool = False

    @property
    def owned_cache(self) -> Dict[str, bool]:
        """Get the owned principals cache (thread-safe read)."""
        with self._lock:
            return self._owned_cache

    @owned_cache.setter
    def owned_cache(self, value: Dict[str, bool]) -> None:
        """Set the owned principals cache (thread-safe write)."""
        with self._lock:
            self._owned_cache = value

    @property
    def quiet_mode(self) -> bool:
        with self._lock:
            return self._quiet_mode

    @quiet_mode.setter
    def quiet_mode(self, value: bool) -> None:
        with self._lock:
            self._quiet_mode = value

    @property
    def show_abuse(self) -> bool:
        with self._lock:
            return self._show_abuse

    @show_abuse.setter
    def show_abuse(self, value: bool) -> None:
        with self._lock:
            self._show_abuse = value

    @property
    def debug_mode(self) -> bool:
        with self._lock:
            return self._debug_mode

    @debug_mode.setter
    def debug_mode(self, value: bool) -> None:
        with self._lock:
            self._debug_mode = value

    @property
    def no_color(self) -> bool:
        with self._lock:
            return self._no_color

    @no_color.setter
    def no_color(self, value: bool) -> None:
        with self._lock:
            self._no_color = value

    @property
    def output_format(self) -> str:
        with self._lock:
            return self._output_format

    @output_format.setter
    def output_format(self, value: str) -> None:
        with self._lock:
            self._output_format = value

    @property
    def severity_filter(self) -> Set[str]:
        with self._lock:
            return self._severity_filter

    @severity_filter.setter
    def severity_filter(self, value: Set[str]) -> None:
        with self._lock:
            self._severity_filter = value

    @property
    def show_progress(self) -> bool:
        with self._lock:
            return self._show_progress

    @show_progress.setter
    def show_progress(self, value: bool) -> None:
        with self._lock:
            self._show_progress = value

    def reset(self):
        """Reset all state to defaults (thread-safe)."""
        with self._lock:
            self._owned_cache.clear()
            self._quiet_mode = False
            self._show_abuse = False
            self._debug_mode = False
            self._no_color = False
            self._output_format = 'table'
            self._severity_filter = set()
            self._show_progress = False


# Singleton instance
config = Config()
