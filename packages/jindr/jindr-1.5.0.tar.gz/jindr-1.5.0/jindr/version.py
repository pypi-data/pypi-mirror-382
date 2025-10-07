"""Version information for JinDr."""

from __future__ import annotations

from importlib import resources

__version__ = (resources.files('jindr') / 'VERSION').read_text().strip()
