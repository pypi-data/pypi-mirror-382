"""Version information for docma."""

from __future__ import annotations

from importlib import resources

__version__ = (resources.files('ollex') / 'VERSION').read_text().strip()
