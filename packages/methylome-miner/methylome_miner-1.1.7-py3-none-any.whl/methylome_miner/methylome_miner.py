"""
MethylomeMiner module contains functions to run the tool to filter, sort methylations and create panmethylome
"""
from pathlib import Path

import click

from .backend import _mine_methylations, _mine_panmethylations


class Mutex(click.Option):
    """
    Edited click Option class to make mutually exclusive options work
    """

    def __init__(self, *args, **kwargs):
        self.not_required_if = kwargs.pop("not_required_if")

        assert self.not_required_if, "'not_required_if' parameter required"
        kwargs["help"] = (kwargs.get("help", "") + "Option is mutually exclusive with " + ", ".join(
            self.not_required_if) + ".").strip()
        super(Mutex, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        current_opt = self.name in opts
        for mutex_opt in self.not_required_if:
            if mutex_opt in opts:
                if current_opt:
                    raise click.UsageError(
                        "Illegal usage: '" + str(self.name) + "' is mutually exclusive with '" + str(mutex_opt) + "'.")
                else:
                    self.prompt = None
        return super(Mutex, self).handle_parse_result(ctx, opts, args)


@click.command()
@click.option(
    "--input_bed_file",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, path_type=Path),
    help="Path to a bedMethyl file with genome-wide single-base methylation data.",
)
@click.option(
    "--input_annot_file",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, path_type=Path),
    help="Path to a file with genome annotation in '.gff' (v3) or '.gbk' file format.",
)
@click.option(
    "--input_bed_dir",
    cls=Mutex, not_required_if=["min_coverage"],
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, path_type=Path),
    help="Path to a directory with bedMethyl files.\n"
         "This option is mutually exclusive with 'min_coverage'.\n"
         "This folder will be used to calculated median coverage from all present bedMethyl files.",
)
@click.option(
    "--min_coverage",
    cls=Mutex, not_required_if=["input_bed_dir"], default=None, type=int,
    help="An integer value of minimum coverage for modified position to be kept.\n"
         "This option is mutually exclusive with 'input_bed_dir'.",
)
@click.option(
    "--min_percent_modified",
    required=False, default=90, type=click.FloatRange(0, 100),
    help="Minimum required percentage of reads supporting base modification.\n"
         "A float value between 0 and 100 inclusive. Default value is 90 %.",
)
@click.option(
    "--work_dir",
    required=False, default=Path(Path.cwd(), "MethylomeMiner_output"),
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True, path_type=Path),
    help="Path to directory for MethylomeMiner outputs.\n"
         "If not provided, 'MethylomeMiner_output' folder will be created in the current working directory.",
)
@click.option(
    "--file_name",
    required=False, default=None,
    help="Custom name for MethylomeMiner outputs.",
)
@click.option(
    "--write_filtered_bed",
    required=False, is_flag=True,
    help="Write filtered bedMethyl file to a new file.",
)
@click.option(
    "--filtered_bed_format",
    required=False, default="csv",
    type=click.Choice(["json", "csv", "tsv", "bed"], case_sensitive=True),
    help="Choose filtered bedMethyl file format.\n"
         "Options: 'json', 'csv', 'tsv', 'bed'.\n"
         "Default format is 'csv'.",
)
@click.option(
    "--split_by_reference",
    required=False, is_flag=True,
    help="Write all outputs (except for filtered bedMethyl file) to separate files based on reference sequence.",
)
def mine_methylations(input_bed_file, input_annot_file, input_bed_dir, min_coverage, min_percent_modified,
                      work_dir, file_name, write_filtered_bed, filtered_bed_format, split_by_reference):
    """
    Filter modified bases stored in bedMethyl file and sort them according to annotation into coding and non-coding.

    Filtration is performed based on requested coverage and the percent of modified bases.
    Sorting is conducted based on provided annotation of the genome. Modified bases are sorted into coding
    (modification is within coding region) and non-coding (modification is in intergenic region) groups.


    :param Path input_bed_file: Path to a bedMethyl file with genome-wide single-base methylation data.
    :param Path input_annot_file: Path to a file with genome annotation in 'gff' (v3) or 'gbk' file format.
    :param Path input_bed_dir: Path to a directory with bedMethyl files.
    :param int min_coverage: An integer value of minimum coverage for modified position to be kept.
    :param float min_percent_modified: Minimum required percentage of reads supporting base modification. Default: 90
    :param Path work_dir: Path to directory for MethylomeMiner outputs. Default: MethylomeMiner_output
    :param str file_name: Custom name for MethylomeMiner outputs.
    :param bool write_filtered_bed: Write filtered bedMethyl file to a new file. Default: False
    :param str filtered_bed_format: File format for filtered bedMethyl file. Default: 'csv'
    :param bool split_by_reference: Write all outputs to separate files based on reference sequence.
    """
    _mine_methylations(input_bed_file, input_annot_file, input_bed_dir, min_coverage, min_percent_modified,
                       work_dir, file_name, write_filtered_bed, filtered_bed_format, split_by_reference)


@click.command()
@click.option(
    "--input_bed_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, path_type=Path),
    help="Path to a directory with bedMethyl files.",
)
@click.option(
    "--input_annot_dir",
    required=True,
    type=click.Path(exists=True, file_okay=False, dir_okay=True, readable=True, resolve_path=True, path_type=Path),
    help="Path to a directory with genome annotations in 'gff' (v3) or 'gbk' file format.",
)
@click.option(
    "--roary_file",
    required=True,
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True, resolve_path=True, path_type=Path),
    help="Path to output file from Roary tool named 'gene_presence_absence.csv'.",
)
@click.option(
    "--min_coverage",
    required=False, default=None, type=int,
    help="An integer value of minimum coverage for modified position to be kept.\n"
         "This option is used only if MethylomeMiner was not previously used for input bedMethyl files"
         "and the results are not present in the 'work_dir' folder.\n"
         "If value is not provided, median coverage will be calculated from files in the 'input_bed_dir' folder.\n",
)
@click.option(
    "--min_percent_modified",
    required=False, default=90, type=click.FloatRange(0, 100),
    help="Minimum required percentage of reads supporting base modification.\n"
         "This option is used only if MethylomeMiner was not previously used for input bedMethyl files"
         "and the results are not present in the 'work_dir' folder.\n"
         "A float value between 0 and 100 inclusive. Default value is 90 %.",
)
@click.option(
    "--matrix_values",
    required=False, default="presence",
    type=click.Choice(["presence", "positions"], case_sensitive=True),
    help="Format of values in the output panmethylome matrix.\n"
         "Options:\n"
         "'presence': '0' value for no detected base modifications, '1' value for detected base modification,"
         "no value for missing gene in the corresponding genome,\n"
         "'positions': a list of genomic positions where base modifications were identified within each pangenome gene"
         "or no value if the gene is missing in the corresponding genome.\n"
         "Default is 'presence' option.",
)
@click.option(
    "--work_dir",
    required=False, default=Path(Path.cwd(), "MethylomeMiner_output"),
    type=click.Path(file_okay=False, dir_okay=True, writable=True, resolve_path=True, path_type=Path),
    help="Path to directory where PanMethylomeMiner will look for results from MethylomeMiner and save all result files.\n"
         "If not provided, 'MethylomeMiner_output' folder will be created in the current working directory.",
)
@click.option(
    "--write_all_results",
    required=False, is_flag=True,
    help="Write all results from MethylomeMiner to files: methylations sorted to coding and non-coding groups, "
         "extended genome annotation with methylations located in coding regions, filtered bedMethyl files.\n",
)
@click.option(
    "--heatmap_type",
    required=False, default=None,
    type=click.Choice(["compact", "full", "both"], case_sensitive=True),
    help="Choose which heatmap(s) of panmethylome should be created.\n"
         "Options:\n"
         "'compact': heatmap of panmethylome in lower resolution without genes' names,\n"
         "'full': heatmap of panmethylome in full resolution with genes' names,\n"
         "'both': both 'compact' and 'full' heatmaps are created.\n"
         "Default behaviour is not to create a heatmap. Heatmaps are created only if matrix values are set to 'presence.'",
)
@click.option(
    "--heatmap_file_format",
    required=False, default="pdf",
    type=click.Choice(["png", "svg", "pdf"], case_sensitive=True),
    help="Set file format of heatmap(s).\n"
         "Options: 'png', 'svg', 'pdf'.\n"
         "Default is 'pdf'.",
)
@click.option(
    "--heatmap_min_percent_presence",
    required=False, default=95, type=click.FloatRange(0, 100),
    help="Minimum required percentage of genomes where are genes present.\n"
         "Default is 95 %."
)
def mine_panmethylations(input_bed_dir, input_annot_dir, roary_file, min_coverage, min_percent_modified,
                         matrix_values, work_dir, write_all_results, heatmap_type, heatmap_file_format,
                         heatmap_min_percent_presence):
    """
    Create panmethylome from bedMethyl files, genome annotation and Roary output.

    :param Path input_bed_dir: Path to a directory with bedMethyl files.
    :param Path input_annot_dir: Path to a directory with genome annotations in 'gff' (v3) or 'gbk' file format.
    :param Path roary_file: Path to output file from Roary tool named 'gene_presence_absence.csv'.
    :param int min_coverage: An integer value of minimum coverage for modified position to be kept.
    :param float min_percent_modified: Minimum required percentage of reads supporting base modification. Default: 90
    :param str matrix_values: Type of values in the output panmethylome matrix. Options: 'presence': '0' value for
        no detected base modifications, '1' value for detected base modification, 'positions': a list of exact
        locations of base modifications within a panmethylome gene; or no value (NaN) for missing gene
        in the corresponding genome. Default is 'presence' option.
    :param Path work_dir: Path to directory for (Pan)MethylomeMiner outputs. Default: MethylomeMiner_output
    :param bool write_all_results: Write all results from (Pan)MethylomeMiner to files. Default: False
    :param str heatmap_type: Choose which heatmap(s) should be created (compact, full, both or none).
        Default: None - no heatmap is created.
    :param str heatmap_file_format: File format of created heatmap(s). Default is 'pdf' format.
    :param float heatmap_min_percent_presence: Minimum required percentage of genomes where are genes present.
    """
    _mine_panmethylations(input_bed_dir, input_annot_dir, roary_file, min_coverage, min_percent_modified,
                          matrix_values, work_dir, write_all_results, heatmap_type, heatmap_file_format,
                          heatmap_min_percent_presence)
