"""Tool results."""

from __future__ import annotations

from typing import TYPE_CHECKING, final

from slurmbench.tool import results as core

import benchmark.topics.assembly.results as asm_res

if TYPE_CHECKING:
    from pathlib import Path


@final
class PlasmidStats(core.Original):
    """Plasmid stats result."""

    # TSV name: "assembly.tsv"
    # * no `.fasta` because Platon removes the extension
    # * no `.gz` because Platon takes an not-compressed FASTA file
    TSV_NAME = asm_res.FastaGZ.FASTA_GZ_NAME.with_suffix("").with_suffix(".tsv")

    def tsv(self, sample_dirname: str | Path) -> Path:
        """Get TSV file."""
        return self._exp_fs_manager.sample_dir(sample_dirname) / self.TSV_NAME
