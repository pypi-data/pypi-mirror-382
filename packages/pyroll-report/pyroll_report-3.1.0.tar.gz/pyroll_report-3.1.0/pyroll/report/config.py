from pyroll.core import config


@config("PYROLL_REPORT")
class Config:
    PRINT_DISK_ELEMENTS = False
    """Whether to include the distinct disk elements into the report."""

    FLOAT_PRECISION = 3
    """Number of decimal digits to print for float values."""

    ANGLE_PRECISION = 3
    """Number of decimal digits to print for float values of angles."""

    TEMPERATURE_PRECISION = 1
    """Number of decimal digits to print for float values of temperatures."""

    RATIO_PRECISION = 4
    """Number of decimal digits to print for float values of ratios."""

    STRAIN_PRECISION = 4
    """Number of decimal digits to print for float values of strains."""

    PLOT_GEOMS = True
    """Whether to plot shapely geometry objects. Otherwise only a property table is printed."""
