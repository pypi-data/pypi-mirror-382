import numpy as np

from pyroll.report import hookimpl
from ..config import Config
from .format import _is_float_like


@hookimpl(specname="property_format")
def temperature_format(name: str, value: object):
    if _is_float_like(value) and "temperature" in name:
        return np.format_float_positional(value, precision=Config.TEMPERATURE_PRECISION, trim="0")


@hookimpl(specname="property_format")
def ratio_format(name: str, value: object):
    if _is_float_like(value) and "ratio" in name:
        return np.format_float_positional(value, precision=Config.RATIO_PRECISION, trim="0")


@hookimpl(specname="property_format")
def strain_format(name: str, value: object):
    if _is_float_like(value) and (
            "strain" in name
            or "elongation" in name
            or "draught" in name
            or "spread" in name
            or "efficiency" in name
    ):
        return np.format_float_positional(value, precision=Config.STRAIN_PRECISION, trim="0")


@hookimpl(specname="property_format")
def angle_format(name: str, value: object):
    if _is_float_like(value) and (("angle" in name or "alpha" in name)) and "relative" not in name:
        return np.format_float_positional(np.rad2deg(value), precision=Config.ANGLE_PRECISION, trim="0")
