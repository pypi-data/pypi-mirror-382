"""Classification topic application module."""

# Due to typer usage:

from __future__ import annotations

from slurmbench.prelude.topic import app as core

from . import description as desc
from . import visitor
from .plasclass import app as plasclass_app
from .plasgraph2 import app as plasgraphtwo_app
from .platon import app as platon_app

APP = core.Topic.new(
    desc.DESCRIPTION,
    visitor.Tools,
    [
        plasclass_app.APP,
        plasgraphtwo_app.APP,
        platon_app.APP,
    ],
)
