"""Assembly topic visitor."""

from typing import final

from slurmbench.prelude.topic import visitor as core

# from .gfa_connector import description as gfa_connector_desc
# from .skesa import description as skesa_desc
from .unicycler import description as unicycler_desc


@final
class Tools(core.Tools):
    """Assembly tools descriptions."""

    UNICYCLER = unicycler_desc.DESCRIPTION.name()

    # SKESA = skesa_desc.DESCRIPTION.name()
    # GFA_CONNECTOR = gfa_connector_desc.DESCRIPTION.name()

    def to_description(self) -> core.Description:
        """Get tool description."""
        match self:
            case Tools.UNICYCLER:
                return unicycler_desc.DESCRIPTION
            # FEATURE: Add SKESA and GFA_CONNECTOR
            # case Tools.SKESA:
            #     return skesa_desc.DESCRIPTION
            # case Tools.GFA_CONNECTOR:
            #     return gfa_connector_desc.DESCRIPTION
