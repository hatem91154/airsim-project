from PyQt5.QtWidgets import QPushButton
from typing import Callable, Optional

from .parameter import Parameter


class ActionParameter(Parameter):
    """Action parameter widget with a button control.
    
    A parameter widget for triggering actions implemented using QPushButton.
    Does not store a value but triggers a callback when clicked.
    
    Attributes:
        name (str): Display name of the parameter
        button (QPushButton): Button widget for triggering the action
    """

    def __init__(self, name: str = "Unnamed", config: Optional[dict] = None) -> None:
        """Initialize the action parameter widget.
        
        Args:
            name: Display name of the parameter (will be used as button text)
            config: Configuration dictionary with optional keys:
                - action: Callback function to execute when clicked
        """
        super().__init__(name, config)
        config = config or {}

        # Hide the label from the base class as we'll use the button text instead
        self.label.hide()
        
        # Create button with parameter name as text
        self.button = QPushButton(self.name)
        self.button.clicked.connect(self.on_clicked)

        # Store action callback if provided
        self._action = config.get("action")
        if self._action and callable(self._action):
            self.register_callback(self._action)

        # Add to existing layout from base class
        self.layout.addWidget(self.button)

    def on_clicked(self) -> None:
        """Handle button click events.
        
        Emits the valueChanged signal with the parameter name and None as value.
        """
        self.valueChanged.emit(self.name, None)

    def set_value(self, value) -> None:
        """Set the parameter value (no-op for action parameters).
        
        Action parameters do not store values, so this is a no-op.
        
        Args:
            value: Ignored
        """
        pass  # Actions don't have values

    def get_value(self) -> None:
        """Get the current parameter value.
        
        Action parameters do not store values, so this always returns None.
        
        Returns:
            None
        """
        return None

    def register_callback(self, callback: Callable[[str, None], None]) -> None:
        """Register a callback to be called when the button is clicked.
        
        Args:
            callback: Function to call when clicked, with signature:
                     callback(parameter_name, None)
        """
        self.valueChanged.connect(callback)
