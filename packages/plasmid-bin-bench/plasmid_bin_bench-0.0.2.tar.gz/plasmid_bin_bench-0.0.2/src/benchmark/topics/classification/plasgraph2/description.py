"""plASgraph2 description."""

from slurmbench.prelude.tool import description as core

import benchmark.topics.classification.description as class_desc

DESCRIPTION = core.Description(
    "PLASGRAPH2",
    "plasgraph2",
    class_desc.DESCRIPTION,
)
