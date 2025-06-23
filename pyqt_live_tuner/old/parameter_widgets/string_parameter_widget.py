from PyQt5.QtWidgets import QLabel, QLineEdit
from typing import Callable

from .parameter_widget import ParameterWidget


class StringParameterWidget(ParameterWidget):
    """
    A parameter widget for string input using QLineEdit.
    Emits valueChanged(name, value) when text changes.
    """

    def __init__(self, name: str = "Unnamed", config: dict = None):
        super().__init__(name, config)
        config = config or {}

        self.value = config.get("initial", "")
        placeholder = config.get("placeholder", "")

        self.label = QLabel(f"{self.name}:")
        self.line_edit = QLineEdit()
        self.line_edit.setText(self.value)
        self.line_edit.setPlaceholderText(placeholder)

        self.line_edit.editingFinished.connect(self.on_text_changed)

        layout = self.layout
        layout.addWidget(self.label)
        layout.addWidget(self.line_edit)

    def on_text_changed(self):
        value = self.line_edit.text()
        if value != self.value:
            self.value = value
            self.emit_value_changed(value)

    def set_value(self, value: str):
        self.value = value
        self.line_edit.setText(value)

    def get_value(self) -> str:
        return self.line_edit.text()

    def register_callback(self, callback: Callable[[str, str], None]) -> None:
        self.valueChanged.connect(callback)
