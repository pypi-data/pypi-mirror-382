"""SKESA assembler items."""

from slurmbench.prelude.tool import description as core

import benchmark.topics.assembly.description as asm_desc

DESCRIPTION = core.Description(
    "GFA_CONNECTOR",
    "gfa-connector",
    asm_desc.DESCRIPTION,
)
