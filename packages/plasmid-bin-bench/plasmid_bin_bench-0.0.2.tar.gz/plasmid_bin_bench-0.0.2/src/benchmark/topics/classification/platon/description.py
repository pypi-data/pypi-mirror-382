"""Platon description module."""

from slurmbench.prelude.tool import description as core

import benchmark.topics.classification.description as class_desc

DESCRIPTION = core.Description("PLATON", "platon", class_desc.DESCRIPTION)
