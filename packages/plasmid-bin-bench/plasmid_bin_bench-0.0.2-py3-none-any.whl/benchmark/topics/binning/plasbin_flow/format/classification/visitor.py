"""PlasBin-flow classification result formatting module."""

from typing import final

from slurmbench.prelude.topic import results as core

import benchmark.topics.classification.visitor as class_visitor

from . import platon, results


@final
class PlasmidnessVisitor(
    core.FormattedVisitor[class_visitor.Tools, results.Plasmidness],
):
    """Plasmidness result visitor."""

    @classmethod
    def convert_fn(
        cls,
        tool: class_visitor.Tools,
    ) -> core.ConvertFn[results.Plasmidness] | core.Error:
        """Get convert function."""

        def _err(tool: class_visitor.Tools) -> core.Error:
            return core.Error(
                "Function to convert classification result to plasmidness result"
                f" is not implemented for `{tool}` ",
            )

        match tool:
            case class_visitor.Tools.PLATON:
                return platon.plasmidness
            case class_visitor.Tools.PLASCLASS:
                return _err(tool)  # FEATURE PlasClass plasmidness convert
            case class_visitor.Tools.PLASGRAPH2:
                return _err(tool)  # FEATURE PlasGraph2 plasmidness convert

    @classmethod
    def result_builder(cls) -> type[results.Plasmidness]:
        """Get result builder."""
        return results.Plasmidness


@final
class SeedsVisitor(core.FormattedVisitor[class_visitor.Tools, results.Seeds]):
    """Seeds result visitor."""

    @classmethod
    def convert_fn(
        cls,
        tool: class_visitor.Tools,
    ) -> core.ConvertFn[results.Seeds] | core.Error:
        """Get convert function."""

        def _err(tool: class_visitor.Tools) -> core.Error:
            return core.Error(
                "Function to convert classification result to plasmidness result"
                f" is not implemented for `{tool}` ",
            )

        match tool:
            case class_visitor.Tools.PLATON:
                return platon.seeds
            case class_visitor.Tools.PLASCLASS:
                return _err(tool)  # FEATURE PlasClass seeds convert
            case class_visitor.Tools.PLASGRAPH2:
                return _err(tool)  # FEATURE PlasGraph2 seeds convert

    @classmethod
    def result_builder(cls) -> type[results.Seeds]:
        """Get result builder."""
        return results.Seeds
