"""Miscellaneous functions."""

from __future__ import annotations

import re
from subprocess import run

__author__ = 'Murray Andrews'

HOSTNAME_RE = re.compile(
    r'^(?=.{1,253}$)([a-z0-9]([-a-z0-9]*[a-z0-9])?)(\.([a-z0-9]([-a-z0-9]*[a-z0-9])?))*$', re.I
)


# ------------------------------------------------------------------------------
def camel_to_snake(name: str) -> str:
    """Convert camel case to snake case."""
    s1 = re.sub(r'(?<!^)(?=[A-Z])', '_', name)
    return s1.lower()


# ------------------------------------------------------------------------------
def is_valid_hostname(hostname: str) -> bool:
    """Check if hostname is valid."""

    return bool(HOSTNAME_RE.match(hostname))


# ------------------------------------------------------------------------------
def get_dirsize(path: str) -> str:
    """Get the size of a directory in hunman readable format."""

    result = run(['du', '-hs', path], text=True, capture_output=True)
    return result.stdout.strip().split()[0]
