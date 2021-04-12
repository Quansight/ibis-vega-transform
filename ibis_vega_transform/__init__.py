"""Ibis-Vega Transform

This module provides a Python implementation of Vega transforms,
evaluated with ibis expressions.
The main function is the ``ibis_vega_transform.apply()`` function.
"""
import json
import os.path as osp

from ._version import __version__, version_info

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


##
# Set global state
##

ipython = IPython.get_ipython()
kernel = getattr(ipython, "kernel", None) if ipython else None

if kernel:
    kernel.comm_manager.register_target("queryibis", query_target_func)
    kernel.comm_manager.register_target(
        "ibis_vega_transform:compiler", compiler_target_function
    )


monkeypatch_altair()

altair.renderers.register("ibis", altair_renderer)
altair.renderers.enable("ibis")

altair.data_transformers.register("ibis", altair_data_transformer)
altair.data_transformers.enable("ibis")

HERE = osp.abspath(osp.dirname(__file__))

with open(osp.join(HERE, "labextension", "package.json")) as fid:
    data = json.load(fid)


def _jupyter_labextension_paths():
    return [{"src": "labextension", "dest": data["name"]}]


def _jupyter_server_extension_points():
    return [{"module": "ibis_vega_transform"}]


def _load_jupyter_server_extension(server_app):
    """Registers the API handler to receive HTTP requests from the frontend extension.

    Parameters
    ----------
    lab_app: jupyterlab.labapp.LabApp
        JupyterLab application instance
    """
    ...


__all__ = [
    "set_fallback",
    "_expr_map",
    "apply",
    "__version__",
    "version_info",
    "_jupyter_labextension_paths",
    "_jupyter_server_extension_points",
    "_load_jupyter_server_extension",
]
