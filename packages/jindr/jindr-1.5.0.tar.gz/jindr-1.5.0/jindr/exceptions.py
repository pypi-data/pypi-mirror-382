"""JinDr exceptions."""

from __future__ import annotations


class JinDrError(Exception):
    """Base class for JinDr errors."""

    pass


class JinDrInternalError(JinDrError):
    """Internal error."""

    def __str__(self):
        """Get string representation."""

        return f'Internal error: {", ".join(str(s) for s in self.args)}'


class JinDrNotFoundError(JinDrError):
    """Missing resource of some kind."""

    def __str__(self):
        """Get string representation."""

        return f'{self.args[0]} not found'
