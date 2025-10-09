from pathlib import Path

import jinja2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

from pyroll.core import Unit, PassSequence, BaseRollPass
from .. import utils
from pyroll.report.pluggy import hookimpl, plugin_manager

_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent, encoding="utf-8")
)

_template = _env.get_template("plots.html")


@hookimpl(specname="unit_display")
def unit_plots_display(unit: Unit):
    plots = [
        utils.get_svg_from_figure(p) if isinstance(p, Figure) else p
        for p in plugin_manager.hook.unit_plot(unit=unit)
    ]

    return _template.render(plots=plots)


@hookimpl(specname="unit_plot")
def roll_forces_plot(unit: Unit):
    if isinstance(unit, PassSequence):
        if any(isinstance(subunit, BaseRollPass) for subunit in unit):
            units = unit.roll_passes
            fig, ax = utils.create_sequence_plot(units)
            ax.set_ylabel(r"roll force $F$")
            ax.set_title("Roll Forces")

            if len(units) > 0:
                indices, forces = np.transpose(
                    [
                        (index, unit.roll_force)
                        for index, unit in enumerate(units)
                        if isinstance(unit, BaseRollPass)
                    ]
                )

                ax.bar(x=indices, height=forces, width=0.8)

            return fig


@hookimpl(specname="unit_plot")
def roll_torques_plot(unit: Unit):
    if isinstance(unit, PassSequence):
        if any(isinstance(subunit, BaseRollPass) for subunit in unit):
            units = unit.roll_passes

            fig, ax = utils.create_sequence_plot(units)
            ax.set_ylabel(r"roll torque $M$")
            ax.set_title("Roll Torques")

            units = list(unit.roll_passes)
            if len(units) > 0:
                x, y = np.transpose(
                    [
                        (index, unit.roll.roll_torque)
                        for index, unit in enumerate(units)
                        if isinstance(unit, BaseRollPass)
                    ]
                )

            ax.bar(x=x, height=y, width=0.8)

            return fig


@hookimpl(specname="unit_plot")
def engine_power_plot(unit: Unit):
    if isinstance(unit, PassSequence):
        if any(isinstance(subunit, BaseRollPass) for subunit in unit):
            units = unit.roll_passes
            fig, ax = utils.create_sequence_plot(units)
            ax.set_ylabel(r"engine power $P_\mathrm{E}$")
            ax.set_title("Engine Power")

            if len(units) > 0:
                x2, y2 = np.transpose(
                    [
                        (index, unit.engine.power)
                        for index, unit in enumerate(units)
                        if isinstance(unit, BaseRollPass)
                    ]
                )

            ax.bar(x=x2, height=y2, width=0.8)

            return fig


@hookimpl(specname="unit_plot")
def strains_plot(unit: Unit):
    if isinstance(unit, PassSequence):
        fig, ax = utils.create_sequence_plot(unit)
        ax.set_ylabel(r"strain $\varphi_\mathrm{V}$")
        ax.set_title("Mean Equivalent Strains")

        units = list(unit)
        if len(units) > 0:
            def gen_seq():
                yield -0.5, units[0].in_profile.strain
                for i, u in enumerate(units):
                    yield i + 0.5, u.out_profile.strain

            x, y = np.transpose(
                list(gen_seq())
            )

            ax.plot(x, y, marker="x")

            return fig


@hookimpl(specname="unit_plot")
def filling_ratios_plot(unit: Unit):
    if isinstance(unit, PassSequence):
        if any(isinstance(subunit, BaseRollPass) for subunit in unit):
            units = unit.roll_passes
            fig, ax = utils.create_sequence_plot(units)
            ax.set_ylabel("Filling Ratio")
            ax2: plt.Axes = ax.twinx()
            ax2.set_ylabel("Filling Error")

            ax.set_title("Filling Ratios and Errors")

            if len(units) > 0:
                x, fr, csfr, fe, cse, tfr, tcsfr = np.transpose(
                    [
                        (
                            index,
                            unit.out_profile.filling_ratio,
                            unit.out_profile.cross_section_filling_ratio,
                            unit.out_profile.filling_error,
                            unit.out_profile.cross_section_error,
                            unit.target_filling_ratio,
                            unit.target_cross_section_filling_ratio,
                        )
                        for index, unit in enumerate(units)
                        if isinstance(unit, BaseRollPass)
                    ]
                )

                ax.plot(x, fr, label="Width Filling Ratio", c="C0")
                ax.plot(x, csfr, label="Cross-Section Filling Ratio", c="C1")
                ax.plot(x, tfr, label="Target", c="C0", ls="--")
                ax.plot(x, tcsfr, label="Target", c="C1", ls="--")
                ax2.plot(x, fe, label="Width Filling Error", c="C0", ls=":")
                ax2.plot(x, cse, label="Cross-Section Error", c="C1", ls=":")

                ax.legend(loc="lower left", ncols=2)
                ax2.legend(loc="lower right")

                return fig


@hookimpl(specname="unit_plot")
def cross_sections_plot(unit: Unit):
    if isinstance(unit, PassSequence):
        if any(isinstance(subunit, BaseRollPass) for subunit in unit):
            units = unit.roll_passes
            fig, ax = utils.create_sequence_plot(units)
            ax.set_ylabel(r"cross section $A_\mathrm{p}$")
            ax.set_title("Profile Cross-Sections")

            if len(units) > 0:
                def gen_seq():
                    yield -0.5, units[0].in_profile.cross_section.area
                    for i, u in enumerate(units):
                        yield i + 0.5, u.out_profile.cross_section.area

                x, y = np.transpose(
                    list(gen_seq())
                )

                ax.plot(x, y, marker="x")

                return fig


@hookimpl(specname="unit_plot")
def roll_pass_plot(unit):
    """Plot roll pass contour and its profiles"""

    if isinstance(unit, BaseRollPass):
        fig: plt.Figure = plt.figure(constrained_layout=True, figsize=(4, 4))
        ax: plt.Axes
        axl: plt.Axes
        ax, axl = fig.subplots(nrows=2, height_ratios=[1, 0.3])
        ax.set_title("In- and Outcoming Profiles")

        ax.set_aspect("equal", "datalim")
        ax.grid(lw=0.5)

        oriented_cl = utils.orient_geometry_to_technology(unit.contour_lines, unit)
        oriented_ipp = utils.orient_geometry_to_technology(unit.in_profile.cross_section, unit)
        oriented_opp = utils.orient_geometry_to_technology(unit.out_profile.cross_section, unit)

        for cl in oriented_cl.geoms:
            c = ax.plot(*cl.xy, color="k", label="roll surface")

        ipp = ax.fill(*oriented_ipp.boundary.xy, alpha=0.5, color="red", label="in profile")
        opp = ax.fill(*oriented_opp.boundary.xy, alpha=0.5, color="blue", label="out profile")

        ipr = ax.fill(*unit.in_profile.equivalent_rectangle.boundary.xy, fill=False, color="red", ls="--",
                      label="in eq. rectangle")
        opr = ax.fill(*unit.out_profile.equivalent_rectangle.boundary.xy, fill=False, color="blue", ls="--",
                      label="out eq. rectangle")

        axl.axis("off")
        axl.legend(handles=c + ipp + opp + ipr + opr, ncols=2, loc="lower center")
        fig.set_layout_engine('constrained')

        return fig
