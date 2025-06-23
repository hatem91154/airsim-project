
from PyQt5.QtCore import pyqtSignal
from typing import Callable

from .parameter_group_widget import ParameterGroupWidget

class LinkedParameterGroup(ParameterGroupWidget):
    """
    A logical group of related parameters.

    Emits groupChanged(group_name, values_dict) when any child parameter changes.
    """

    groupChanged = pyqtSignal(str, dict)

    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        self.group_name = title

    def add_parameter(self, widget):
        """
        Add a widget and hook its signal to the group emitter.
        """
        super().add_parameter(widget)
        widget.valueChanged.connect(self._on_any_value_changed)

    def _on_any_value_changed(self, *_):
        """
        Called when any parameter in the group changes.
        Emits groupChanged with the full set of values.
        """
        self.groupChanged.emit(self.group_name, self.get_values())

    def register_callback(self, callback: Callable[[str, dict], None]):
        """
        Register a function to handle group-level changes.

        Args:
            callback: function(group_name: str, values: dict)
        """
        self.groupChanged.connect(callback)
