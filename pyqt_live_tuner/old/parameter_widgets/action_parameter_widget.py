from PyQt5.QtWidgets import QPushButton
from typing import Callable

from .parameter_widget import ParameterWidget

class ActionParameterWidget(ParameterWidget):
    """
    A parameter widget that acts as a button to trigger actions like Load or Save.
    Emits valueChanged(name, value) when clicked.
    """

    def __init__(self, name: str = "Button", config: dict = None):
        super().__init__(name, config)
        config = config or {}

        self.label = config.get("label", "Click Me")

        self.button = QPushButton(self.label)
        self.button.clicked.connect(self.on_click)

        self.layout.addWidget(self.button)

    def on_click(self):
        """Emit a signal when the button is clicked."""
        self.emit_value_changed(True)

    def set_value(self, value: bool):
        """No-op for button widget."""
        pass

    def get_value(self) -> bool:
        """Always returns False as this is a trigger button."""
        return False

    def register_callback(self, callback: Callable[[str, bool], None]) -> None:
        self.valueChanged.connect(callback)
