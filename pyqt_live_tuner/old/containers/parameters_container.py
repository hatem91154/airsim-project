"""Container module for organizing parameter widgets and groups.

This module provides the ParametersContainer class, which organizes and manages
parameter widgets and parameter groups in a scrollable area. It supports both
individual parameter widgets and logical groupings of related parameters.
"""

from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QFrame

from pyqt_live_tuner.parameter_widgets import ParameterWidget
from pyqt_live_tuner.parameter_groups import ParameterGroupWidget


class ParametersContainer(QScrollArea):
    """A scrollable container for organizing parameter widgets and groups.
    
    This class provides a scrollable panel that organizes parameter widgets and
    parameter groups. It manages the layout and provides methods for getting and
    setting parameter values across all contained widgets and groups.
    
    Attributes:
        _widgets (dict): Dictionary mapping parameter names to ParameterWidget instances
        _groups (list): List of ParameterGroupWidget instances
        layout (QVBoxLayout): The layout for arranging widgets and groups
        container (QWidget): The container widget that holds the layout
    """

    def __init__(self, parent=None):
        """Initialize the parameters container.
        
        Args:
            parent: The parent widget (default: None)
        """
        super().__init__(parent)
        self.setWidgetResizable(True)

        self.container = QWidget()
        self.setWidget(self.container)

        self.layout = QVBoxLayout()
        self.container.setLayout(self.layout)

        self._widgets = {}  # name → ParameterWidget
        self._groups = []   # list of ParameterGroupWidgets

    def add_param(self, widget: ParameterWidget):
        """Add a parameter widget to the container.
        
        Adds a parameter widget to the container and wraps it in a styled frame.
        If a widget with the same name already exists, it will be replaced.
        
        Args:
            widget: The parameter widget to add
        """
        self._widgets[widget.name] = widget

        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        inner_layout = QVBoxLayout()
        inner_layout.addWidget(widget)
        frame.setLayout(inner_layout)

        self.layout.addWidget(frame)

    def add_group(self, group: ParameterGroupWidget):
        """Add a parameter group to the container.
        
        Adds a parameter group widget to the container. Parameter groups
        allow for logical organization of related parameters.
        
        Args:
            group: The parameter group widget to add
        """
        self._groups.append(group)
        self.layout.addWidget(group)

    def get_values(self) -> dict:
        """Get values from all parameters and parameter groups.
        
        Collects values from all parameter widgets and parameter groups
        in the container. Group values are nested under their respective titles.
        
        Returns:
            A dictionary containing all parameter values, with group values
            nested under their respective group titles
        """
        result = {}

        # Top-level individual parameters
        for name, widget in self._widgets.items():
            result[name] = widget.get_value()

        # Groups — return as nested dicts under group titles
        for group in self._groups:
            result[group.title()] = group.get_values()

        return result

    def set_values(self, values: dict):
        """Set values for all parameters and parameter groups.
        
        Applies values to parameter widgets and parameter groups in the container.
        Group values should be nested dictionaries under their respective titles.
        
        Args:
            values: Dictionary of values to apply, with group values nested
                  under their respective group titles
        """
        # Apply to top-level widgets
        for name, val in values.items():
            if name in self._widgets:
                self._widgets[name].set_value(val)

        # Check if group title exists, and pass nested dict to that group
        for group in self._groups:
            if group.title() in values and isinstance(values[group.title()], dict):
                group.set_values(values[group.title()])
                
    # Provide property access to internal collections for compatibility
    @property
    def widgets(self):
        """Property that provides read access to the internal widgets dictionary.
        
        Returns:
            Dictionary mapping parameter names to ParameterWidget instances
        """
        return self._widgets
        
    @property
    def groups(self):
        """Property that provides read access to the internal groups list.
        
        Returns:
            List of ParameterGroupWidget instances
        """
        return self._groups