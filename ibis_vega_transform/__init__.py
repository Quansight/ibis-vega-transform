"""Ibis-Vega Transform

This module provides a Python implementation of Vega transforms,
evaluated with ibis expressions.
The main function is the ``ibis_vega_transform.apply()`` function.
"""

# Third party imports
import altair
import IPython

# Local imports
from .altair_data_transformer import altair_data_transformer
from .altair_monkeypatch import monkeypatch_altair
from .altair_renderer import altair_renderer
from .compiler import compiler_target_function
from .core import apply
from .globals import _expr_map, set_fallback, enable_debug, disable_debug
from .query import query_target_func


# Constants
def _to_version_info(version):
    """Convert a version string to a number and string tuple."""
    parts = []
    for part in version.split("."):
        try:
            part = int(part)
        except ValueError:
            pass

        parts.append(part)

    return tuple(parts)


__version__ = "5.2.2"
version_info = _to_version_info(__version__)


##
# Set global state
##

ipython = IPython.get_ipython()
kernel = getattr(ipython, "kernel", None) if ipython else None

if kernel:
    kernel.comm_manager.register_target("queryibis", query_target_func)
    kernel.comm_manager.register_target(
        "ibis-vega-transform:compiler", compiler_target_function
    )


monkeypatch_altair()

altair.renderers.register("ibis", altair_renderer)
altair.renderers.enable("ibis")

altair.data_transformers.register("ibis", altair_data_transformer)
altair.data_transformers.enable("ibis")

__all__ = ["set_fallback", "_expr_map", "apply", "__version__", "version_info"]
