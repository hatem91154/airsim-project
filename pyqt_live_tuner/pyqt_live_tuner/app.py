"""Application entry point for PyQt Live Tuner.

This module provides the LiveTunerApp class (formerly ApplicationBuilder), which serves
as the main entry point for creating PyQt Live Tuner applications.
"""

import qdarktheme
from PyQt5.QtWidgets import QApplication
from typing import Optional, List

from .main_window import MainWindow

# Singleton QApplication instance
class _QApplicationSingleton:
    """Singleton implementation for the QApplication.
    
    Ensures only one QApplication instance exists throughout the application.
    """
    _instance: Optional[QApplication] = None
    
    @classmethod
    def instance(cls) -> QApplication:
        """Get the singleton QApplication instance.
        
        Creates a new QApplication if one doesn't exist yet.
        
        Returns:
            The QApplication instance
        """
        if cls._instance is None:
            cls._instance = QApplication([])
        return cls._instance
    
    @classmethod
    def exec(cls) -> int:
        """Execute the application's event loop.
        
        Returns:
            The exit code from the event loop
        """
        return cls.instance().exec_()


class LiveTunerApp:
    """Main entry point for creating and running PyQt Live Tuner applications.
    
    This class provides a simple way to create and run parameter tuning
    applications with a single line of code.
    
    Attributes:
        main_window (MainWindow): The main application window
    """
    
    def __init__(self, title: str = "My Application", use_dark_theme: bool = True):
        """Initialize a new PyQt Live Tuner application.
        
        Args:
            title: Title for the application window (default: "My Application")
            use_dark_theme: Whether to use the dark theme (default: True)
        """
        self._app = _QApplicationSingleton
        
        # Create QApplication first
        app_instance = self._app.instance()
        
        # Set up dark theme after QApplication creation
        if use_dark_theme:
            qdarktheme.setup_theme("dark")
            
        self.main_window = MainWindow(title)
    
    def run(self) -> int:
        """Show the main window and start the application event loop.
        
        Returns:
            The exit code from the event loop
        """
        self.main_window.show()
        return self._app.exec()
