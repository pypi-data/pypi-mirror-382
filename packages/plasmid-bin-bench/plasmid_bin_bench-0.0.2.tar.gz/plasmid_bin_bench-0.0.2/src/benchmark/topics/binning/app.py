"""Topic application module."""

# Due to typer usage:

from __future__ import annotations

from slurmbench.topic import app as core

from . import description as desc
from . import visitor
from .pangebin_once import app as pg_once_app

APP = core.Topic.new(
    desc.DESCRIPTION,
    visitor.Tools,
    [pg_once_app.APP],
)
