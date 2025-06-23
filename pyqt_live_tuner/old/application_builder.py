"""Application builder module for PyQt Live Tuner.

This module provides a simple facade for creating and running PyQt Live Tuner
applications. It handles the creation of the QApplication instance and
sets up the dark theme for consistent styling across the application.
"""

from typing import Optional, Tuple
from PyQt5.QtWidgets import QApplication
from pyqt_live_tuner import ParametersContainer
from pyqt_live_tuner import ConfigurationsContainer

import qdarktheme

from .main_application import MainApplication

# Create a singleton QApplication instance
_Application = QApplication([])
qdarktheme.setup_theme("dark")


class ApplicationBuilder:
    """Builder class for creating and running PyQt Live Tuner applications.

    This class simplifies the creation of PyQt Live Tuner applications by handling
    the QApplication instantiation and main window setup. It ensures there's only
    one QApplication instance regardless of how many ApplicationBuilder instances
    are created.

    Attributes:
        main_window (MainApplication): The main application window
        _app (QApplication): Reference to the singleton QApplication instance
    """

    def __init__(self, title: str = "My Application"):
        """Initialize the application builder.

        Args:
            title: Title for the main application window (default: "My Application")
        """
        self._app = _Application
        self.main_window: Optional[MainApplication] = MainApplication(title=title)

    def run(self):
        """Build the main window and launch the application.

        Shows the main window and starts the Qt event loop, which blocks
        until the application is closed.
        """
        self.main_window.show()
        self._app.exec()
