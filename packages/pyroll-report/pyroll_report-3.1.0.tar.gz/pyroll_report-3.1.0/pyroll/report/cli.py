import logging
from pathlib import Path

from .report import report as report_func
from pyroll.cli import State
import click
from .config import Config

DEFAULT_REPORT_FILE = "report.html"


@click.command()
@click.option(
    "-f", "--file",
    help="File to write to.",
    type=click.Path(dir_okay=False, path_type=Path),
    default=DEFAULT_REPORT_FILE, show_default=True
)
@click.option(
    "-d/-nd", "--print-disk-elements/--no-print-disk-elements",
    default=None,
    help="Whether to print the disk elements in the report "
         "(overrides the PRINT_DISK_ELEMENTS config value, the default is to not override the config).",
)
@click.option(
    "-g/-ng", "--plot-geoms/--no-plot-geoms",
    default=None,
    help="Whether to plot shapely geometry objects in the report "
         "(overrides the PLOT_GEOMS config value, the default is to not override the config).",
)
@click.option(
    "--float-precision",
    type=int,
    default=None,
    help="Number of decimal digits to print for float values "
         "(overrides the FLOAT_PRECISION config value, the default is to not override the config).",
)
@click.option(
    "--temperature-precision",
    type=int,
    default=None,
    help="Number of decimal digits to print for float values of temperatures "
         "(overrides the TEMPERATURE_PRECISION config value, the default is to not override the config).",
)
@click.option(
    "--ratio-precision",
    type=int,
    default=None,
    help="Number of decimal digits to print for float values of ratios "
         "(overrides the RATIO_PRECISION config value, the default is to not override the config).",
)
@click.option(
    "--angle-precision",
    type=int,
    default=None,
    help="Number of decimal digits to print for float values of angles "
         "(overrides the ANGLE_PRECISION config value, the default is to not override the config).",
)
@click.option(
    "--strain-precision",
    type=int,
    default=None,
    help="Number of decimal digits to print for float values of strains "
         "(overrides the STRAIN_PRECISION config value, the default is to not override the config).",
)
@click.pass_obj
def report(state: State, file: Path, print_disk_elements, plot_geoms, float_precision, temperature_precision,
           ratio_precision, angle_precision, strain_precision):
    """Generates a HTML report from the simulation results and writes it to FILE."""
    log = logging.getLogger(__name__)

    if print_disk_elements is not None:
        Config.PRINT_DISK_ELEMENTS = print_disk_elements

    if plot_geoms is not None:
        Config.PLOT_GEOMS = plot_geoms

    if float_precision is not None:
        Config.FLOAT_PRECISION = float_precision

    if temperature_precision is not None:
        Config.TEMPERATURE_PRECISION = temperature_precision

    if ratio_precision is not None:
        Config.RATIO_PRECISION = ratio_precision

    if angle_precision is not None:
        Config.ANGLE_PRECISION = angle_precision

    if strain_precision is not None:
        Config.STRAIN_PRECISION = strain_precision

    rendered = report_func(state.sequence)

    file.write_text(rendered, encoding='utf-8')
    log.info(f"Wrote report to: {file.absolute()}")
