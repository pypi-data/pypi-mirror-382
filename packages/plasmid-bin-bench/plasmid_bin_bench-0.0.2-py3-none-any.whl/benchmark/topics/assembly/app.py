"""Concrete topic application module."""

# Due to typer usage:

from __future__ import annotations

from slurmbench.prelude.topic import app as core

import benchmark.topics.assembly.description as assembly_desc
import benchmark.topics.assembly.unicycler.app as unicycler_app

from . import visitor

APP = core.Topic.new(assembly_desc.DESCRIPTION, visitor.Tools, [unicycler_app.APP])
