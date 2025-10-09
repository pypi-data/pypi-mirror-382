"""Samples module."""

from enum import StrEnum

from slurmbench.prelude import samples as core


class TSVHeader(StrEnum):
    """Custom samples file header."""

    SAMPLE_UID = core.TSVHeader.SAMPLE_UID
    SHORT_READS = "short_reads"
