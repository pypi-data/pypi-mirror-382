"""Topics module."""

from typing import final

from slurmbench.prelude.topics import visitor as core

from .assembly import description as asm_desc
from .assembly import visitor as asm_visitor
from .binning import description as binning_desc
from .binning import visitor as binning_visitor
from .classification import description as class_desc
from .classification import visitor as class_visitor


@final
class Topics(core.Topics):
    """Topic names."""

    ASSEMBLY = asm_desc.DESCRIPTION.name()
    CLASSIFICATION = class_desc.DESCRIPTION.name()
    BINNING = binning_desc.DESCRIPTION.name()

    def to_description(self) -> core.Description:
        """Get topic description."""
        match self:
            case Topics.ASSEMBLY:
                return asm_desc.DESCRIPTION
            case Topics.CLASSIFICATION:
                return class_desc.DESCRIPTION
            case Topics.BINNING:
                return binning_desc.DESCRIPTION

    def tools(self) -> type[core.Tools]:
        """Get topic tools."""
        match self:
            case Topics.ASSEMBLY:
                return asm_visitor.Tools
            case Topics.CLASSIFICATION:
                return class_visitor.Tools
            case Topics.BINNING:
                return binning_visitor.Tools
