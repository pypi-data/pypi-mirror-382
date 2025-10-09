from typing import Union, Optional

from matplotlib.figure import Figure

from pyroll.report.pluggy import hookspec
from pyroll.core import Unit


@hookspec
def unit_display(unit: Unit, level: int) -> str:
    """Return HTML code as str which displays the given unit.
    Multiple implementations will be included sequentially into the report.
    Other return types as HTML str are possible, if respective hook wrappers for conversion exist."""


@hookspec
def unit_plot(unit: Unit) -> Union[Figure, str]:
    """Generate a matplotlib figure or SVG code visualizing a unit.
    All loaded hook implementations are listed in the report."""


@hookspec(firstresult=True)
def property_format(name: str, value: object, owner: Optional[object]) -> str:
    """
    Format the value of a property as string for display in the report. This hook is first result.
    :param name: the name of the property to format
    :param value: the value of the property to format
    :param owner: the owner of the property to format, may be None
    """

