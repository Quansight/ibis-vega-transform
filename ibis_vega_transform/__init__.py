"""Ibis-Vega Transform

This module provides a Python implementation of Vega transforms,
evaluated with ibis expressions.
The main function is the ``ibis_vega_transform.apply()`` function.
"""
__version__ = "0.1.0.dev0"
__all__ = ["apply", "transforms"]

from .core import apply
from . import transforms
