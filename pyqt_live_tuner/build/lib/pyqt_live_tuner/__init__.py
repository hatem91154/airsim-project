"""PyQt Live Tuner package.

A framework for creating parameter tuning applications with PyQt5.
"""

# Import core components
from .app import LiveTunerApp
from .main_window import MainWindow
from .file_handler import FileHandler

# Import from subpackages
from .parameters import *
from .groups import *
from .panels import *

# For backward compatibility
ApplicationBuilder = LiveTunerApp

__all__ = [
    # Core components
    'LiveTunerApp',
    'MainWindow',
    'FileHandler',
    'ApplicationBuilder',  # For backward compatibility
]

# Add all exports from subpackages
__all__.extend(parameters.__all__)
__all__.extend(groups.__all__)
__all__.extend(panels.__all__)