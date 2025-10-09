"""PlasClass description."""

from slurmbench.prelude.tool import description as core

import benchmark.topics.classification.description as class_desc

DESCRIPTION = core.Description(
    "PLASCLASS",
    "plasclass",
    class_desc.DESCRIPTION,
)
