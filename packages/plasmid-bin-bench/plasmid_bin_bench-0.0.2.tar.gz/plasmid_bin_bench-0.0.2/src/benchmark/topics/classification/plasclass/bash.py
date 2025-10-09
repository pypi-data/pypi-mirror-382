"""Platon Bash script logics."""

from collections.abc import Iterator
from pathlib import Path
from typing import final

from slurmbench.prelude.tool import bash as core

import benchmark.topics.assembly.results as asm_res
import benchmark.topics.classification.plasclass.results as plasclass_res


@final
class FastaInputLinesBuilder(core.Argument[asm_res.FastaGZ]):
    """Fasta input bash lines builder."""

    FASTA_GZ_VAR = core.BashVar("FASTA_GZ")

    FASTA_VAR = core.BashVar("FASTA")
    OUTFILE_VAR = core.BashVar("OUTFILE")

    def __fasta_gz_file(self) -> Path:
        """Return a gzipped FASTA path with sample name is a sh variable."""
        return self._input_result.fasta_gz(
            self._input_data_smp_sh_fs_manager.sample_dir().name,
        )

    def __fasta_tmp_file(self) -> Path:
        """Return a tmp FASTA path with sample name is a sh variable."""
        return (
            self._work_smp_sh_fs_manager.sample_dir()
            / self._input_result.FASTA_GZ_NAME.with_suffix("")
        )

    def init_lines(self) -> Iterator[str]:
        """Get shell input init lines."""
        yield self.FASTA_GZ_VAR.set_path(self.__fasta_gz_file())
        yield self.FASTA_VAR.set_path(self.__fasta_tmp_file())
        yield self.OUTFILE_VAR.set_path(
            plasclass_res.PlasmidProbabilities(self._work_exp_fs_manager).tsv(
                self._work_smp_sh_fs_manager.sample_dir().name,
            ),
        )
