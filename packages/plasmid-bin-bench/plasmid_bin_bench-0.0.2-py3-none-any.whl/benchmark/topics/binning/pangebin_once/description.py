"""Tool description."""

from slurmbench.prelude.tool import description as core

import benchmark.topics.binning.description as desc

DESCRIPTION = core.Description(
    "PANGEBIN_ONCE",
    "pangebin-once",
    desc.DESCRIPTION,
)
