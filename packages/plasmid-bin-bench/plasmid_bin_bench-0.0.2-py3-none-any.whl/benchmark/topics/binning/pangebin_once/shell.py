"""Concrete tool Bash script logics."""

from collections.abc import Iterator
from pathlib import Path
from typing import final

from slurmbench.prelude.tool import bash as core

import benchmark.topics.assembly.results as asm_res
from benchmark.topics.binning.plasbin_flow.format.classification import (
    results as fmt_class_res,
)


@final
class GFAInputLinesBuilder(core.Argument[asm_res.AsmGraphGZ]):
    """GFA input bash lines builder."""

    GFA_GZ_VAR = core.BashVar("GFA")

    def __gfa_gz_file(self) -> Path:
        """Return a gzipped GFA path with sample name is a sh variable."""
        return self._input_result.gfa_gz(
            self._input_data_smp_sh_fs_manager.sample_dir().name,
        )

    def init_lines(self) -> Iterator[str]:
        """Get shell input init lines."""
        yield self.GFA_GZ_VAR.set_path(self.__gfa_gz_file())


@final
class SeedsInputLinesBuilder(core.Argument[fmt_class_res.Seeds]):
    """Seeds input bash lines builder."""

    SEEDS_VAR = core.BashVar("SEEDS")

    def __plasbin_seeds_file(self) -> Path:
        """Return a gzipped GFA path with sample name is a sh variable."""
        return self._input_result.tsv(
            self._input_data_smp_sh_fs_manager.sample_dir().name,
        )

    def init_lines(self) -> Iterator[str]:
        """Get shell input init lines."""
        yield self.SEEDS_VAR.set_path(self.__plasbin_seeds_file())

    def close_lines(self) -> Iterator[str]:
        """Get shell input close lines."""
        yield from ()


@final
class PlasmidnessInputLinesBuilder(core.Argument[fmt_class_res.Plasmidness]):
    """Plasmidness input bash lines builder."""

    PLASMIDNESS_VAR = core.BashVar("PLASMIDNESS")

    def __plasbin_plasmidness_file(self) -> Path:
        """Return a gzipped GFA path with sample name is a sh variable."""
        return self._input_result.tsv(
            self._input_data_smp_sh_fs_manager.sample_dir().name,
        )

    def init_lines(self) -> Iterator[str]:
        """Get shell input init lines."""
        yield self.PLASMIDNESS_VAR.set_path(self.__plasbin_plasmidness_file())
