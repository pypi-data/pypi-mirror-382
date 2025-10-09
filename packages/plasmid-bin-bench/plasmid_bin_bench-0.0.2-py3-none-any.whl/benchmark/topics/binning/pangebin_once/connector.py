"""Concrete tool connector module."""

from __future__ import annotations

from typing import final

from slurmbench.prelude.tool import connector as core

import benchmark.topics.assembly.results as asm_res
import benchmark.topics.assembly.visitor as asm_visitor
import benchmark.topics.classification.visitor as class_visitor
from benchmark.topics.binning.plasbin_flow.format.classification import (
    results as fmt_class_res,
)
from benchmark.topics.binning.plasbin_flow.format.classification import (
    visitor as fmt_class_visitor,
)

from . import description as desc
from . import shell as sh


@final
class Names(core.Names):
    """Argument names."""

    GFA = "GFA"
    SEEDS = "SEEDS"
    PLASMIDNESS = "PLASMIDNESS"

    def topic_tools(self) -> type[core.Tools]:
        """Get topic tools."""
        match self:
            case Names.GFA:
                return asm_visitor.Tools
            case Names.SEEDS:
                return class_visitor.Tools
            case Names.PLASMIDNESS:
                return class_visitor.Tools


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
class SeedsArg(core.Arg[Names, class_visitor.Tools, fmt_class_res.Seeds]):
    """Seeds argument."""

    @classmethod
    def name(cls) -> Names:
        """Get name."""
        return Names.SEEDS

    @classmethod
    def tools_type(cls) -> type[class_visitor.Tools]:
        """Get tools type."""
        return class_visitor.Tools

    @classmethod
    def result_visitor(cls) -> type[fmt_class_visitor.SeedsVisitor]:
        """Get result visitor."""
        return fmt_class_visitor.SeedsVisitor

    @classmethod
    def sh_lines_builder_type(cls) -> type[sh.SeedsInputLinesBuilder]:
        """Get shell lines builder type."""
        return sh.SeedsInputLinesBuilder


@final
class PlasmidnessArg(core.Arg[Names, class_visitor.Tools, fmt_class_res.Plasmidness]):
    """Plasmidness argument."""

    @classmethod
    def name(cls) -> Names:
        """Get name."""
        return Names.PLASMIDNESS

    @classmethod
    def tools_type(cls) -> type[class_visitor.Tools]:
        """Get tools type."""
        return class_visitor.Tools

    @classmethod
    def result_visitor(cls) -> type[fmt_class_visitor.PlasmidnessVisitor]:
        """Get result visitor."""
        return fmt_class_visitor.PlasmidnessVisitor

    @classmethod
    def sh_lines_builder_type(
        cls,
    ) -> type[sh.PlasmidnessInputLinesBuilder]:
        """Get shell lines builder type."""
        return sh.PlasmidnessInputLinesBuilder


@final
class Arguments(core.Arguments[Names]):
    """Concrete tool arguments."""

    @classmethod
    def arg_types(cls) -> list[type[core.Arg]]:
        """Get list of arg types."""
        return [
            GFAArg,
            SeedsArg,
            PlasmidnessArg,
        ]


@final
class Connector(core.WithArguments[Names]):
    """Concrete tool connector."""

    @classmethod
    def description(cls) -> core.Description:
        """Get description."""
        return desc.DESCRIPTION

    @classmethod
    def arguments_type(cls) -> type[Arguments]:
        """Get arguments type."""
        return Arguments
