"""Connector for Unicycler."""

# Due to typer usage:

from __future__ import annotations

from typing import final

from slurmbench.prelude.tool import connector as core

from . import bash
from . import description as desc


@final
class Connector(core.OnlyOptions):
    """Unicycler connector."""

    @classmethod
    def commands_type(cls) -> type[bash.OnlyOptions]:
        """Get custom commands type."""
        return bash.OnlyOptions

    @classmethod
    def description(cls) -> core.Description:
        """Get description."""
        return desc.DESCRIPTION
