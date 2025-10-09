import html
from typing import Sequence, Collection

import numpy as np

from pyroll.core.repr import ReprMixin
from pyroll.report.pluggy import hookimpl, plugin_manager
from .properties import render_properties_table, DoNotPrint
import shapely.geometry

from ..config import Config
from ..utils import plot_shapely_geom


def _is_float_like(value: object):
    return isinstance(value, float) or (
            isinstance(value, np.ndarray) and np.isscalar(value) and np.issubdtype(value.dtype, np.floating))


@hookimpl(specname="property_format", trylast=True)
def default_format(value: object):
    return html.escape(str(value))


@hookimpl(specname="property_format")
def int_format(value: object):
    if isinstance(value, int) and not isinstance(value, bool):
        return "{:d}".format(value)


@hookimpl(specname="property_format")
def float_format(value: object):
    if _is_float_like(value):
        if np.isclose(value, 0):
            return None

        order = np.log10(np.abs(value)) // 3
        if not np.isfinite(order):
            return np.format_float_positional(value)
        exp = int(order) * 3
        mantissa = value / 10 ** exp
        return f"{np.format_float_positional(mantissa, trim='0', precision=Config.FLOAT_PRECISION)}e{exp:+03d}"


@hookimpl(specname="property_format")
def collection_format(name: str, value: object, owner: object):
    if (
            isinstance(value, Collection)
            and not isinstance(value, str)
    ):
        return ", ".join([plugin_manager.hook.property_format(name=name, value=e, owner=owner) for e in value])


@hookimpl(specname="property_format")
def repr_mixin_format(value: object):
    if isinstance(value, ReprMixin):
        return f"""
        <details open>
            <summary>{str(value)}</summary>
            <div>
                {render_properties_table(value)}
            </div>
        </details>
        """


# noinspection PyTypeChecker
@hookimpl(specname="property_format")
def shapely_format(value: object):
    if isinstance(value, (shapely.geometry.Polygon, shapely.geometry.LineString, shapely.geometry.MultiLineString, shapely.geometry.MultiPolygon)):
        if Config.PLOT_GEOMS:
            return f"""
            <details open>
                <summary>{str(value)}</summary>
                <div class="row align-items-center">
                    <div class="col-4">
                        {plot_shapely_geom(value)}
                    </div>
                    <div class="col-8">
                        {render_properties_table(value)}
                    </div>
                </div>
            </details>
            """
        else:
            return f"""
            <details open>
                <summary>{str(value)}</summary>
                <div>
                    {render_properties_table(value)}
                </div>
            </details>
            """


@hookimpl(specname="property_format")
def disk_elements_format(name: str, value: object):
    if isinstance(value, Sequence) and name == "disk_elements":
        if not Config.PRINT_DISK_ELEMENTS:
            raise DoNotPrint()

        displays = "\n".join(
            [
                d
                for u in value
                for d in plugin_manager.hook.unit_display(unit=u, level=6)
            ]
        )

        if displays:
            return f"""
            <details>
                <summary>Disk Elements (click to expand)</summary>
                <div>
                    {displays}
                </div>
            </details>
            """

        raise DoNotPrint()
