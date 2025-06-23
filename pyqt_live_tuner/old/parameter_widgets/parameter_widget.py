# views/parameter_widgets/parameter_widget.py
"""Base parameter widget classes for PyQt Live Tuner.

This module provides the abstract base classes for parameter widgets that
enable real-time tuning of various parameter types within the application.
Each widget provides a consistent interface for getting and setting values,
as well as signaling when values change.
"""

from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

from pyqt_live_tuner.logger import logger

class ParameterWidget(QWidget):
    """Abstract base class for all parameter editor widgets.
    
    Each widget represents one tunable parameter (e.g. float, bool, string).
    This base class handles the common functionality shared by all parameter 
    widgets, including layout management, name storage, and value change signaling.
    
    Attributes:
        name (str): Display name of the parameter
        config (dict): Configuration options for the parameter
        layout (QHBoxLayout): Horizontal layout for the widget components
        valueChanged (pyqtSignal): Signal emitted when the parameter value changes,
            with signature valueChanged(parameter_name, new_value)
    """

    valueChanged = pyqtSignal(str, object)  # (parameter_name, new_value)

    def __init__(self, name: str, config: dict = None):
        """Initialize the parameter widget base.
        
        Args:
            name: Display name of the parameter
            config: Configuration dictionary with optional keys:
                - tooltip: Hover text to display (optional)
                - disabled: Whether the widget should be disabled (optional, default: False)
        """
        super().__init__()
        self.name = name
        self.config = config or {}

        self.layout = QHBoxLayout()
        self.setLayout(self.layout)

        # Optional tooltip support
        if "tooltip" in self.config:
            self.setToolTip(self.config["tooltip"])

        # Optional disable state
        if self.config.get("disabled", False):
            self.setDisabled(True)

    def set_value(self, value):
        """Set the parameter's current value.
        
        Must be implemented by subclasses to update the widget's value
        and visual representation.
        
        Args:
            value: The new value to set for the parameter
            
        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError

    def get_value(self):
        """Get the parameter's current value.
        
        Must be implemented by subclasses to return the current parameter value.
        
        Returns:
            The current value of the parameter
            
        Raises:
            NotImplementedError: If the subclass doesn't implement this method
        """
        raise NotImplementedError

    def emit_value_changed(self, value):
        """Emit a valueChanged signal with the parameter name and new value.
        
        This method logs the value change and emits the valueChanged signal
        to notify listeners of the change.
        
        Args:
            value: The new parameter value to emit
        """
        logger.debug(f"[{self.name}] Value changed → {value}")
        self.valueChanged.emit(self.name, value)
