"""Platon connector module."""

from __future__ import annotations

from typing import final

from slurmbench.prelude.tool import connector as core

import benchmark.topics.assembly.results as asm_res
import benchmark.topics.assembly.visitor as asm_visitor

from . import description as desc
from . import shell as sh


@final
class Names(core.Names):
    """Platon names."""

    GENOME = "GENOME"

    def topic_tools(self) -> type[core.Tools]:
        """Get topic tools."""
        match self:
            case Names.GENOME:
                return asm_visitor.Tools


@final
class GenomeArg(core.Arg[Names, asm_visitor.Tools, asm_res.FastaGZ]):
    """Genome argument."""

    @classmethod
    def name(cls) -> Names:
        """Get name."""
        return Names.GENOME

    @classmethod
    def tools_type(cls) -> type[asm_visitor.Tools]:
        """Get tools type."""
        return asm_visitor.Tools

    @classmethod
    def result_visitor(cls) -> type[asm_res.FastaGZVisitor]:
        """Get result visitor."""
        return asm_res.FastaGZVisitor

    @classmethod
    def sh_lines_builder_type(cls) -> type[sh.GenomeInputLinesBuilder]:
        """Get shell lines builder type."""
        return sh.GenomeInputLinesBuilder


@final
class Arguments(core.Arguments[Names]):
    """Platon arguments."""

    @classmethod
    def arg_types(cls) -> list[type[core.Arg]]:
        """Get list of arg types."""
        return [
            GenomeArg,
        ]


@final
class Connector(core.WithArguments[Names]):
    """Platon connector."""

    @classmethod
    def description(cls) -> core.Description:
        """Get tool description."""
        return desc.DESCRIPTION

    @classmethod
    def arguments_type(cls) -> type[Arguments]:
        """Get arguments type."""
        return Arguments
