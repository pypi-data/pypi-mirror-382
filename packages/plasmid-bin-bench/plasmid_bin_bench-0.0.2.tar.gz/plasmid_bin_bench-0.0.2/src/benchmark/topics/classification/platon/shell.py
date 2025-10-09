"""Platon Bash script logics."""

from collections.abc import Iterator
from pathlib import Path
from typing import final

from slurmbench.prelude.tool import bash as core

import benchmark.topics.assembly.results as asm_res


@final
class GenomeInputLinesBuilder(core.Argument[asm_res.FastaGZ]):
    """Genome input bash lines builder."""

    GENOME_VAR = core.BashVar("GENOME")
    FASTA_GZ_VAR = core.BashVar("FASTA_GZ")

    def __fasta_gz_file(self) -> Path:
        """Return a gzipped FASTA path with sample name is a sh variable."""
        return self._input_result.fasta_gz(
            self._work_smp_sh_fs_manager.sample_dir().name,
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
        yield self.GENOME_VAR.set_path(self.__fasta_tmp_file())
