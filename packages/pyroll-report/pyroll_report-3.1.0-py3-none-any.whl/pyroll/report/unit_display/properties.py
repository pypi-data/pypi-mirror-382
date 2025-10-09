from pathlib import Path

import jinja2

from pyroll.core import Unit
from pyroll.core.repr import ReprMixin
from pyroll.report.pluggy import hookimpl, plugin_manager

_env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent, encoding="utf-8")
)


class DoNotPrint(Exception):
    pass


def try_format_property(name: str, value: object, owner: object):
    try:
        return plugin_manager.hook.property_format(name=name, value=value, owner=owner)
    except (TypeError, ValueError, DoNotPrint):
        return None


def render_properties_table(instance: ReprMixin):
    template = _env.get_template("properties.html")

    properties = [
        (n.replace("_", " "), s) for n, v in instance.__attrs__.items()
        if (s := try_format_property(n, v, instance)) is not None
    ]

    return template.render(
        properties=properties,
    )


@hookimpl(specname="unit_display")
def unit_properties_display(unit: Unit, level: int):
    return render_properties_table(unit)
