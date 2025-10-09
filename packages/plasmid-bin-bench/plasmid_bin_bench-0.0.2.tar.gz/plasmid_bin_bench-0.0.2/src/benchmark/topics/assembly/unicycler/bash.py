"""Platon Bash script logics."""

from collections.abc import Iterator
from typing import final

from slurmbench.prelude.tool import bash as core

from benchmark import samples as smp


@final
class OnlyOptions(core.OnlyOptions):
    """Unicycler custom OnlyOption bash command class."""

    SRR_ID_VAR = core.BashVar("SRR_ID")

    def init_lines(self) -> Iterator[str]:
        """Get shell input init lines."""
        yield self.SRR_ID_VAR.set(
            core.get_sample_attribute(
                self.data_exp_fs_manager().samples_tsv(),
                smp.TSVHeader.SHORT_READS,
            ),
        )
