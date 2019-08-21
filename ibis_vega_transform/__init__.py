"""Ibis-Vega Transform

This module provides a Python implementation of Vega transforms,
evaluated with ibis expressions.
The main function is the ``ibis_vega_transform.apply()`` function.
"""
from .core import apply
from . import transforms
from .altair import display_queries


__all__ = ["apply", "transforms", "display_queries"]