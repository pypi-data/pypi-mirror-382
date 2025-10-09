"""Concrete tool application module."""

from __future__ import annotations

from slurmbench.prelude.tool import app as core

from . import connector

APP = core.new(connector.Connector)
