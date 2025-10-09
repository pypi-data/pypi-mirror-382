"""plASgraph2 results."""

from __future__ import annotations

from pathlib import Path
from typing import final

from slurmbench.prelude.tool import results as core


@final
class PlasmidProbabilities(core.Original):
    """Plasmid probabilities result."""

    CSV_NAME = Path("plasmid_probabilities.csv")

    def csv(self, sample_dirname: str | Path) -> Path:
        """Get plasmid probabilities CSV file."""
        return self._exp_fs_manager.sample_dir(sample_dirname) / self.CSV_NAME
