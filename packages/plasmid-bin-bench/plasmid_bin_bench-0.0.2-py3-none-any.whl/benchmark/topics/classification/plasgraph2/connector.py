"""plASgraph2 connector module."""

from __future__ import annotations

from typing import final

from slurmbench.prelude.tool import connector as core

import benchmark.topics.assembly.results as asm_res
import benchmark.topics.assembly.visitor as asm_visitor

from . import description as desc
from . import shell as sh


@final
class Names(core.Names):
    """Argument names."""

    GFA = "GFA"

    def topic_tools(self) -> type[core.Tools]:
        """Get topic tools."""
        match self:
            case Names.GFA:
                return asm_visitor.Tools


@final
class GFAArg(core.Arg[Names, asm_visitor.Tools, asm_res.AsmGraphGZ]):
    """GFA argument."""

    @classmethod
    def name(cls) -> Names:
        """Get name."""
        return Names.GFA

    @classmethod
    def tools_type(cls) -> type[asm_visitor.Tools]:
        """Get tools type."""
        return asm_visitor.Tools

    @classmethod
    def result_visitor(cls) -> type[asm_res.AsmGraphGZVisitor]:
        """Get result visitor."""
        return asm_res.AsmGraphGZVisitor

    @classmethod
    def sh_lines_builder_type(cls) -> type[sh.GFAInputLinesBuilder]:
        """Get shell lines builder type."""
        return sh.GFAInputLinesBuilder


@final
class Arguments(core.Arguments[Names]):
    """Platon arguments."""

    @classmethod
    def arg_types(cls) -> list[type[core.Arg]]:
        """Get list of arg types."""
        return [
            GFAArg,
        ]


@final
class Connector(core.WithArguments[Names]):
    """Platon connector."""

    @classmethod
    def description(cls) -> core.Description:
        """Get description."""
        return desc.DESCRIPTION

    @classmethod
    def arguments_type(cls) -> type[Arguments]:
        """Get arguments type."""
        return Arguments
