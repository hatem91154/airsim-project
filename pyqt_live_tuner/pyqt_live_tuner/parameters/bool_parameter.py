from PyQt5.QtWidgets import QCheckBox
from typing import Callable, Optional

from .parameter import Parameter


class BoolParameter(Parameter):
    """Boolean parameter widget with a checkbox control.
    
    A parameter widget for boolean values implemented using a QCheckBox.
    Provides simple true/false selection with a label.
    
    Attributes:
        name (str): Display name of the parameter
        value (bool): Current parameter value
        checkbox (QCheckBox): Checkbox control for toggling the value
    """

    def __init__(self, name: str = "Unnamed", config: Optional[dict] = None) -> None:
        """Initialize the boolean parameter widget.
        
        Args:
            name: Display name of the parameter
            config: Configuration dictionary with optional keys:
                - initial: Initial value (default: False)
        """
        super().__init__(name, config)
        config = config or {}

        self.value = config.get("initial", False)

        # Create checkbox (using existing label from base class)
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.value)
        self.checkbox.stateChanged.connect(self.on_toggle)

        # Add to existing layout from base class
        self.layout.addWidget(self.checkbox)

    def on_toggle(self, state: int) -> None:
        """Handle checkbox state changes.
        
        Updates the value and emits the valueChanged signal when the checkbox is toggled.
        
        Args:
            state: The new checkbox state (Qt.Checked or Qt.Unchecked)
        """
        checked = bool(state)
        if checked != self.value:
            self.value = checked
            self.valueChanged.emit(self.name, self.value)

    def set_value(self, value: bool) -> None:
        """Set the parameter value programmatically.
        
        Updates the widget's value and checkbox state, and emits the valueChanged signal.
        
        Args:
            value: The new boolean value to set
        """
        if bool(value) != self.value:
            self.value = bool(value)
            self.checkbox.setChecked(self.value)
            self.valueChanged.emit(self.name, self.value)

    def get_value(self) -> bool:
        """Get the current parameter value.
        
        Returns:
            The current boolean value of the parameter
        """
        return self.value

    def register_callback(self, callback: Callable[[str, bool], None]) -> None:
        """Register a callback to be called when the value changes.
        
        Args:
            callback: Function to call when value changes, with signature:
                     callback(parameter_name, parameter_value)
        """
        self.valueChanged.connect(callback)
