"""PlasBin-flow classification result formatting module."""

from pathlib import Path
from typing import final

from slurmbench.prelude.tool import results as core


@final
class Plasmidness(core.Formatted):
    """Plasmidness PlasBin-flow formatted result."""

    TSV_NAME = Path("pbf_plasmidness.tsv")

    def tsv(self, sample_dirname: str | Path) -> Path:
        """Get plasmidness TSV file."""
        return self._exp_fs_manager.sample_dir(sample_dirname) / self.TSV_NAME

    def check(self, sample_item: core.Sample) -> core.SampleStatus:
        """Check input(s)."""
        if self.tsv(sample_item.uid()).exists():
            return core.SampleSuccess.OK
        return core.SampleError.NOT_RUN


@final
class Seeds(core.Formatted):
    """Seeds PlasBin-flow formatted result."""

    TSV_NAME = Path("pbf_seeds.tsv")

    def tsv(self, sample_dirname: str | Path) -> Path:
        """Get seeds TSV file."""
        return self._exp_fs_manager.sample_dir(sample_dirname) / self.TSV_NAME

    def check(self, sample_item: core.Sample) -> core.SampleStatus:
        """Check input(s)."""
        if self.tsv(sample_item.uid()).exists():
            return core.SampleSuccess.OK
        return core.SampleError.NOT_RUN
