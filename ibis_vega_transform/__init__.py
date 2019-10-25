"""Ibis-Vega Transform

This module provides a Python implementation of Vega transforms,
evaluated with ibis expressions.
The main function is the ``ibis_vega_transform.apply()`` function.
"""
import altair
import IPython

from .altair_data_transformer import altair_data_transformer
from .altair_monkeypatch import monkeypatch_altair
from .altair_renderer import altair_renderer
from .compiler import compiler_target_function
from .core import apply
from .query import query_target_func
from .globals import set_fallback, _expr_map

__all__ = ["set_fallback", "_expr_map", "apply"]


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
