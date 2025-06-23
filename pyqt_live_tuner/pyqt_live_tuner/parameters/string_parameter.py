from PyQt5.QtWidgets import QLineEdit
from typing import Callable, Optional

from .parameter import Parameter


class StringParameter(Parameter):
    """String parameter widget with text input field.
    
    A parameter widget for string input implemented using QLineEdit.
    Provides text input with optional placeholder text.
    
    Attributes:
        name (str): Display name of the parameter
        value (str): Current parameter value
        line_edit (QLineEdit): Text input widget
    """

    def __init__(self, name: str = "Unnamed", config: Optional[dict] = None) -> None:
        """Initialize the string parameter widget.
        
        Args:
            name: Display name of the parameter
            config: Configuration dictionary with optional keys:
                - initial: Initial value (default: empty string)
                - placeholder: Placeholder text for the input field
        """
        super().__init__(name, config)
        config = config or {}

        self.value = config.get("initial", "")
        placeholder = config.get("placeholder", "")

        # Create line edit (using existing label from base class)
        self.line_edit = QLineEdit()
        self.line_edit.setText(self.value)
        self.line_edit.setPlaceholderText(placeholder)
        self.line_edit.editingFinished.connect(self.on_text_changed)

        # Add to existing layout from base class
        self.layout.addWidget(self.line_edit)

    def on_text_changed(self) -> None:
        """Handle text change events from the line edit.
        
        Updates the value and emits the valueChanged signal when the text changes.
        """
        value = self.line_edit.text()
        if value != self.value:
            self.value = value
            self.valueChanged.emit(self.name, value)

    def set_value(self, value: str) -> None:
        """Set the parameter value programmatically.
        
        Updates the widget's value and line edit text, and emits the valueChanged signal.
        
        Args:
            value: The new string value to set
        """
        self.value = value
        self.line_edit.setText(value)
        self.valueChanged.emit(self.name, value)

    def get_value(self) -> str:
        """Get the current parameter value.
        
        Returns:
            The current string value of the parameter
        """
        return self.line_edit.text()

    def register_callback(self, callback: Callable[[str, str], None]) -> None:
        """Register a callback to be called when the value changes.
        
        Args:
            callback: Function to call when value changes, with signature:
                     callback(parameter_name, parameter_value)
        """
        self.valueChanged.connect(callback)
