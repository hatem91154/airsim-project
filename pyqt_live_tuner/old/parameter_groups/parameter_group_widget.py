# views/parameter_groups/parameter_group_widget.py

from PyQt5.QtWidgets import QGroupBox, QVBoxLayout
from typing import Dict

from pyqt_live_tuner.parameter_widgets import ParameterWidget


class ParameterGroupWidget(QGroupBox):
    """
    Base class for a group of ParameterWidgets displayed in a vertical QGroupBox.

    - Stores a mapping of parameter name → widget
    - Provides helper methods to get/set all values
    - Subclasses can override behavior (e.g. signal handling)
    """

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.setLayout(QVBoxLayout())
        self.widgets: Dict[str, ParameterWidget] = {}

    def add_parameter(self, widget: ParameterWidget):
        """
        Add a ParameterWidget to this group.

        Args:
            widget (ParameterWidget): An instance of a parameter widget.
        """
        self.widgets[widget.name] = widget
        self.layout().addWidget(widget)

    def get_value(self, name: str):
        """
        Get the value of a specific parameter widget by name.

        Args:
            name (str): The name of the parameter.

        Returns:
            The value of the parameter widget.
        """
        return self.widgets[name].get_value() if name in self.widgets else None

    def set_value(self, name: str, value):
        """
        Set the value of a specific parameter widget by name.

        Args:
            name (str): The name of the parameter.
            value: The value to set.
        """
        if name in self.widgets:
            self.widgets[name].set_value(value)
        else:
            raise ValueError(f"Parameter '{name}' not found in this group.")    
    
    def get_values(self) -> dict:
        """
        Get current values from all contained widgets.

        Returns:
            dict: {parameter_name: value}
        """
        return {name: widget.get_value() for name, widget in self.widgets.items()}

    def set_values(self, values: dict):
        """
        Set values for any matching widgets in this group.

        Args:
            values (dict): {parameter_name: value}
        """
        for name, value in values.items():
            if name in self.widgets:
                self.widgets[name].set_value(value)
