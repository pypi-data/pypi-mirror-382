"""PlasBin-flow result formatting module."""

import gzip

import pandas as pd
from Bio import SeqIO
from slurmbench.prelude.tool import results as core

import benchmark.topics.assembly.visitor as asm_visitor
import benchmark.topics.classification.platon.results as platon_res
from benchmark.topics.classification.platon import connector

from . import results


def plasmidness(
    platon_data_exp_fs_manager: core.ExpFSDataManager,
    sample_item: core.Sample,
) -> results.Plasmidness:
    """Convert Platon result into plasmidness PlasBin-flow input."""
    plasmidness_res = platon_res.PlasmidStats(platon_data_exp_fs_manager)
    pbf_plasmidness_res = results.Plasmidness(
        platon_data_exp_fs_manager,
    )

    platon_genome_arg = core.get_arg(
        platon_data_exp_fs_manager,
        connector.GenomeArg,
    )
    if isinstance(platon_genome_arg, core.InvalidToolNameError):
        _err_msg = (
            f"Invalid tool name `{platon_genome_arg.invalid_tool_name()}`"
            f" for argument name `{platon_genome_arg.arg_name()}`."
        )
        raise TypeError(_err_msg)

    asm_data_fs_manager = core.ExpFSDataManager(
        platon_data_exp_fs_manager.root_dir(),
        asm_visitor.Tools(platon_genome_arg.tool()).to_description(),
        platon_genome_arg.exp_name(),
    )
    fasta_gz = (
        platon_genome_arg.result_visitor()
        .result_builder()(asm_data_fs_manager)
        .fasta_gz(sample_item.uid())
    )

    with plasmidness_res.tsv(sample_item.uid()).open() as tsv_file:
        set_of_platon_ids = {line.split("\t")[0] for line in tsv_file}

    with (
        pbf_plasmidness_res.tsv(sample_item.uid()).open("w") as tsv_file,
        gzip.open(fasta_gz, "rt") as fasta_gz_file,
    ):
        for record in SeqIO.parse(fasta_gz_file, "fasta"):
            if record.name in set_of_platon_ids:
                tsv_file.write(f"{record.name}\t1\n")
            else:
                tsv_file.write(f"{record.name}\t0\n")

    return pbf_plasmidness_res


def seeds(
    platon_data_exp_fs_manager: core.ExpFSDataManager,
    sample_item: core.Sample,
) -> results.Seeds:
    """Convert plasmid stats to PBF format."""
    seeds_res = platon_res.PlasmidStats(platon_data_exp_fs_manager)
    pbf_seeds_res = results.Seeds(
        platon_data_exp_fs_manager,
    )

    platon_seeds_stats_df = pd.read_csv(
        seeds_res.tsv(sample_item.uid()),
        sep="\t",
    )

    platon_seeds_stats_df.to_csv(
        pbf_seeds_res.tsv(sample_item.uid()),
        columns=["ID"],
        header=False,
        sep="\t",
        index=False,
    )
    return pbf_seeds_res
