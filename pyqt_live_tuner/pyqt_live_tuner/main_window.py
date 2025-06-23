"""Main window module for PyQt Live Tuner.

This module provides the MainWindow class (formerly MainApplication), which serves
as the primary window for PyQt Live Tuner applications. It handles parameter panels,
configuration panels, and menu functionality for saving and loading configurations.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QGridLayout, QLabel, QFileDialog, QAction, QMenuBar, QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from typing import Optional, Dict, Tuple

from .panels.parameter_panel import ParameterPanel
from .panels.config_panel import ConfigPanel
from .parameters.parameter import Parameter
from .groups.parameter_group import ParameterGroup
from .file_handler import FileHandler
from .logger import logger


class MainWindow(QMainWindow):
    """Main window for PyQt Live Tuner applications.
    
    This class provides the primary window interface for PyQt Live Tuner
    applications, handling parameter panels, configuration panels,
    and file operations for saving and loading parameter configurations.
    
    Attributes:
        _param_panel (ParameterPanel): Container for parameter widgets
        _config_panel (ConfigPanel): Container for configuration widgets
        layout (QGridLayout): Main grid layout for the window
        _file_handler (FileHandler): Handler for file operations
        _panels (Dict): Dictionary tracking panels by position
    """
    
    def __init__(
        self,
        title: str = "My Application",
    ):
        """Initialize the main application window.
        
        Args:
            title: Title for the application window (default: "My Application")
        """
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumWidth(450)

        # Setup file handler
        self._file_handler = FileHandler()

        # Layout setup
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QGridLayout()
        central_widget.setLayout(self.layout)

        # Panel tracking
        self._panels = {}  # Dictionary to track panels by position


        # Menu
        self._setup_menu()

    def _setup_menu(self):
        """Set up the application menu bar.
        
        Creates the menu bar with File menu options for generating,
        loading, saving, and saving configurations as new files.
        """
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = menu_bar.addMenu("File")

    def _make_action(self, label: str, slot):
        """Create a menu action with the given label and slot function.
        
        Args:
            label: Text to display in the menu
            slot: Function to call when the action is triggered
            
        Returns:
            QAction: The created menu action
        """
        action = QAction(label, self)
        action.triggered.connect(slot)
        return action

    def add_panel(self, panel: QWidget, position: Tuple[int, int], name: Optional[str] = None, 
                row_span: int = 1, col_span: int = 1, alignment: Optional[int] = None):
        """Add any widget panel to the grid at a specified position.
        
        Args:
            panel: Any QWidget to add as a panel
            position: Tuple of (row, column) where to place the panel in the grid
            name: Optional label text to display above the panel
            row_span: Number of rows the panel should span (default: 1)
            col_span: Number of columns the panel should span (default: 1)
            alignment: Qt alignment flag (default: None)
        
        Returns:
            The position where the panel was placed
        """
        row, col = position
        
        
        # Add label if provided
        if name:
            label = QLabel(name)
            self.layout.addWidget(label, row, col, 1, col_span)
            row += 1  # Place panel below the label
        
        # Add the panel
        if alignment:
            self.layout.addWidget(panel, row, col, row_span, col_span, alignment)
        else:
            self.layout.addWidget(panel, row, col, row_span, col_span)
        
        # Track the panel
        panel_position = (row, col)
        self._panels[panel_position] = {
            'widget': panel,
            'row_span': row_span,
            'col_span': col_span,
            'name': name
        }
        
        return panel_position
