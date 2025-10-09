"""plASgraph2 Bash script logics."""

from collections.abc import Iterator
from pathlib import Path
from typing import final

from slurmbench.prelude.tool import bash as core

import benchmark.topics.assembly.results as asm_res
import benchmark.topics.classification.plasgraph2.results as plasgraphtwo_res


@final
class GFAInputLinesBuilder(core.Argument[asm_res.AsmGraphGZ]):
    """GFA input bash lines builder."""

    GFA_GZ_VAR = core.BashVar("GFA")

    OUTFILE_VAR = core.BashVar("OUTFILE")

    def __gfa_gz_file(self) -> Path:
        """Return a gzipped GFA path with sample name is a sh variable."""
        return self._input_result.gfa_gz(
            self._input_data_smp_sh_fs_manager.sample_dir().name,
        )

    def init_lines(self) -> Iterator[str]:
        """Get shell input init lines."""
        yield self.GFA_GZ_VAR.set_path(self.__gfa_gz_file())
        yield self.OUTFILE_VAR.set_path(
            plasgraphtwo_res.PlasmidProbabilities(self._work_exp_fs_manager).csv(
                self._work_smp_sh_fs_manager.sample_dir().name,
            ),
        )
