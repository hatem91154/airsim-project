"""Panels for PyQt Live Tuner.

This package provides panel classes for organizing parameters and configuration widgets.
"""

from .parameter_panel import ParameterPanel
from .config_panel import ConfigPanel

__all__ = [
    'ParameterPanel',
    'ConfigPanel',
]