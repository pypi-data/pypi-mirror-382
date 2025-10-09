"""Root pbfbench application module."""

# Due to typer usage:

from __future__ import annotations

from slurmbench.prelude import app as core_app

from .topics import visitor as topics_visitor
from .topics.assembly import app as assembly_app
from .topics.binning import app as binning_app
from .topics.classification import app as class_app

APP = core_app.new(
    "pbfbench",
    "PlasBin-flow benchmarking framework",
    topics_visitor.Topics,
    (
        assembly_app.APP,
        class_app.APP,
        binning_app.APP,
    ),
)
