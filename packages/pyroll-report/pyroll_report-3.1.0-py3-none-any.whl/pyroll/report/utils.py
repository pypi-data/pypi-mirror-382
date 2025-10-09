import re
import shapely
import numpy as np

from io import StringIO
from typing import Sequence, List
from shapely.affinity import rotate
from shapely import LineString, Geometry
from matplotlib import pyplot as plt
from matplotlib.ticker import FixedLocator, FixedFormatter
from pyroll.core import Unit, BaseRollPass


def orient_geometry_to_technology(geom: List[Geometry] | Geometry, unit: BaseRollPass):
    orientation = unit.orientation

    if isinstance(orientation, str):
        if orientation.lower() in ["horizontal", "h", "y"]:
            orientation = 0
        elif orientation.lower() in ["vertical", "v"]:
            orientation = 90
        elif orientation.lower() in ["antiy", "ay"]:
            orientation = 180

    if orientation != 0:
        if isinstance(geom, List):
            return [rotate(cl, angle=orientation, origin=(0, 0)) for cl in geom]
        else:
            return rotate(geom, angle=orientation, origin=(0, 0))
    return geom


def create_sequence_plot(units: Sequence[Unit]):
    """Creates a styled base figure for use in sequence plots.
    The x-axis ticks will be labeled with the unit labels and indices."""
    fig: plt.Figure = plt.figure(constrained_layout=True, figsize=(8, 4))
    ax: plt.Axes = fig.subplots()

    indices = np.arange(len(units))
    ax.xaxis.set_major_locator(FixedLocator(indices))
    ax.xaxis.set_major_formatter(
        FixedFormatter([f"{i}: {p}" for i, p in zip(indices, units)]))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
    ax.grid()

    return fig, ax


def resize_svg_to_100_percent(svg: str) -> str:
    svg = re.sub(r'height="[\d.\w]*?"', 'height="100%"', svg)
    svg = re.sub(r'width="[\d.\w]*?"', 'width="100%"', svg)
    return svg


def get_svg_from_figure(fig: plt.Figure) -> str:
    with StringIO() as buf:
        fig.savefig(buf, format="svg")
        plt.close(fig)
        return buf.getvalue()


def plot_shapely_geom(geom: shapely.Geometry):
    fig: plt.Figure = plt.figure(figsize=(2, 2))
    ax: plt.Axes = fig.add_subplot()
    ax.axis("off")
    ax.set_aspect("equal")
    fig.patch.set_alpha(0)

    try:
        if isinstance(geom, shapely.LineString):
            ax.plot(*geom.xy, c="k")
        elif isinstance(geom, shapely.Polygon):
            ax.fill(*geom.boundary.xy, c="k", alpha=0.5)
            ax.fill(*geom.boundary.xy, c="k", fill=False)
        elif isinstance(geom, shapely.MultiLineString):
            for g in geom.geoms:
                ax.plot(*g.xy, c="k")
        elif isinstance(geom, shapely.MultiPolygon):
            for g in geom.geoms:
                ax.fill(*g.boundary.xy, c="k", alpha=0.5)
                ax.fill(*g.boundary.xy, c="k", fill=False)
    except NotImplementedError:
        return ""

    fig.set_layout_engine('constrained')
    return resize_svg_to_100_percent(get_svg_from_figure(fig))
