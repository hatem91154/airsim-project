"""Parameter groups for PyQt Live Tuner.

This package provides classes for organizing parameters into logical groups.
"""

from .parameter_group import ParameterGroup
from .linked_parameter_group import LinkedParameterGroup

__all__ = [
    'ParameterGroup',
    'LinkedParameterGroup',
]