"""Main application module for PyQt Live Tuner.

This module provides the MainApplication class, which serves as the primary
window for PyQt Live Tuner applications. It handles parameter containers,
configuration containers, and menu functionality for saving and loading
parameter configurations.
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QFileDialog, QAction, QMenuBar, QMessageBox
)
from PyQt5.QtGui import QIcon
from typing import Optional, Tuple, Dict, Any
import json, os

from .parameter_widgets import ParameterWidget
from .containers.parameters_container import ParametersContainer
from .containers.configurations_container import ConfigurationsContainer
from .logger import logger

class FileHandler:
    """Handler for file operations related to parameter configurations.
    
    This class is responsible for loading and saving parameter configurations to JSON files.
    It abstracts the file I/O operations from the main application class.
    
    Attributes:
        _last_save_path (str): Path of the last saved configuration file
    """
    
    def __init__(self):
        """Initialize the file handler."""
        self._last_save_path = None
        
    def save_config(self, values: Dict[str, Any], file_path: Optional[str] = None) -> Optional[str]:
        """Save parameter values to a JSON configuration file.
        
        Args:
            values: Parameter values to save
            file_path: Path to save to (if None, uses last saved path or prompts user)
            
        Returns:
            Path of the saved file, or None if save was canceled or failed
        """
        path = file_path or self._last_save_path
        if not path:
            return None
            
        try:
            with open(path, "w") as f:
                json.dump(values, f, indent=2)
            self._last_save_path = path
            return path
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return None
            
    def load_config(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Load parameter values from a JSON configuration file.
        
        Args:
            file_path: Path to the file to load
            
        Returns:
            Dictionary of loaded values, or None if load failed
        """
        if not file_path or not os.path.exists(file_path):
            return None
            
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
            return data
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return None
            
    def get_save_path(self) -> str:
        """Get the path of the last saved file.
        
        Returns:
            Path of the last saved file, or None if no file has been saved
        """
        return self._last_save_path
        
    def set_save_path(self, path: str) -> None:
        """Set the path for future save operations.
        
        Args:
            path: New save path to use
        """
        self._last_save_path = path


class MainApplication(QMainWindow):
    """Main window for PyQt Live Tuner applications.
    
    This class provides the primary window interface for PyQt Live Tuner
    applications, handling parameter containers, configuration containers,
    and file operations for saving and loading parameter configurations.
    
    Attributes:
        _parameters_container (ParametersContainer): Container for parameter widgets
        _configurations_container (ConfigurationsContainer): Container for configuration widgets
        layout (QVBoxLayout): Main vertical layout for the window
        _file_handler (FileHandler): Handler for file operations
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
        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        # Containers
        self._parameters_container: Optional[ParametersContainer] = None
        self._configurations_container: Optional[ConfigurationsContainer] = None

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

        file_menu.addAction(self._make_action("Generate", self._generate_config))
        file_menu.addAction(self._make_action("Load", self._load_config))
        file_menu.addAction(self._make_action("Save", self._save_config))
        file_menu.addAction(self._make_action("Save As...", self._save_config_as))

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

    def set_parameters_container(self, container: ParametersContainer, name: str = "Parameters"):
        """Set the parameters container for the application.
        
        Replaces any existing parameters container with the new one
        and adds it to the layout with a label.
        
        Args:
            container: Parameters container to add
            name: Label text to display above the container (default: "Parameters")
        """
        if self._parameters_container:
            self.layout.removeWidget(self._parameters_container)
            self._parameters_container.deleteLater()
        self._parameters_container = container
        self.layout.addWidget(QLabel(name))
        self.layout.addWidget(container)

    def set_configurations_container(self, container: ConfigurationsContainer, name: str = "Configurations"):
        """Set the configurations container for the application.
        
        Replaces any existing configurations container with the new one
        and adds it to the layout with a label.
        
        Args:
            container: Configurations container to add
            name: Label text to display above the container (default: "Configurations")
        """
        if self._configurations_container:
            self.layout.removeWidget(self._configurations_container)
            self._configurations_container.deleteLater()
        self._configurations_container = container
        self.layout.addWidget(QLabel(name))
        self.layout.addWidget(container)

    def add_parameter(self, param: ParameterWidget):
        """Add a parameter widget to the parameters container.
        
        Creates a parameters container if one doesn't exist yet.
        
        Args:
            param: Parameter widget to add
        """
        if self._parameters_container is None:
            container = ParametersContainer()
            self.set_parameters_container(container, "Parameters")
        self._parameters_container.add_param(param)

    def add_parameter_group(self, group: ParameterWidget):
        """Add a parameter group to the parameters container.
        
        Creates a parameters container if one doesn't exist yet.
        
        Args:
            group: Parameter group widget to add
        """
        if self._parameters_container is None:
            container = ParametersContainer()
            self.set_parameters_container(container, "Parameters")
        self._parameters_container.add_group(group)

    def add_configuration_widget(self, widget: QWidget, label: Optional[str] = None):
        """Add a widget to the configurations container.
        
        Creates a configurations container if one doesn't exist yet.
        Optionally adds a label above the widget.
        
        Args:
            widget: Widget to add to the configurations container
            label: Optional label text to display above the widget
        """
        if self._configurations_container is None:
            container = ConfigurationsContainer()
            self.set_configurations_container(container, "Configurations")
        if label:
            self._configurations_container.layout.addWidget(QLabel(label))
        self._configurations_container.layout.addWidget(widget)

    def _generate_config(self):
        """Generate a new configuration file from current parameter values.
        
        Opens a file dialog to select the save location, then saves the
        current parameter values as a JSON file.
        """
        if not self._parameters_container:
            return
            
        values = self._parameters_container.get_values()
        file_path, _ = QFileDialog.getSaveFileName(self, "Generate Config", "", "JSON Files (*.json)")
        
        if file_path:
            self._file_handler.set_save_path(file_path)
            if self._file_handler.save_config(values, file_path):
                QMessageBox.information(self, "Generated", f"Configuration saved to:\n{file_path}")

    def _load_config(self):
        """Load a configuration file and apply the values to the parameters.
        
        Opens a file dialog to select the configuration file, then loads
        the values and applies them to the parameters container.
        """
        if not self._parameters_container:
            return
            
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Config", "", "JSON Files (*.json)")
        if not file_path:
            return
            
        data = self._file_handler.load_config(file_path)
        if data:
            self._parameters_container.set_values(data)
            QMessageBox.information(self, "Loaded", f"Loaded configuration from:\n{file_path}")

    def _save_config(self):
        """Save the current parameter values to a configuration file.
        
        If a file has been saved/loaded previously, saves to that location.
        Otherwise, calls _save_config_as() to prompt for a file location.
        """
        if not self._parameters_container:
            return
            
        if self._file_handler.get_save_path():
            values = self._parameters_container.get_values()
            file_path = self._file_handler.save_config(values)
            if file_path:
                self.statusBar().showMessage(f"Configuration saved to: {file_path}")
        else:
            self._save_config_as()

    def _save_config_as(self):
        """Save the current parameter values to a new configuration file.
        
        Opens a file dialog to select the save location, then saves the
        current parameter values as a JSON file.
        """
        if not self._parameters_container:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Config As", "", "JSON Files (*.json)")
        if file_path:
            self._file_handler.set_save_path(file_path)
            self._save_config()
