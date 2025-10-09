"""Binning topic visitor."""

from typing import final

from slurmbench.prelude.topic import visitor as core

from .pangebin_once import description as pgbonce_desc


@final
class Tools(core.Tools):
    """Plasmidness tools descriptions."""

    PANGEBIN_ONCE = pgbonce_desc.DESCRIPTION.name()

    def to_description(self) -> core.Description:
        """Get tool description."""
        match self:
            case Tools.PANGEBIN_ONCE:
                return pgbonce_desc.DESCRIPTION
