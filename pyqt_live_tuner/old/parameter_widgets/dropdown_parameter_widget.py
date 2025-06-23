from PyQt5.QtWidgets import QLabel, QComboBox
from typing import Callable, Optional, List

from pyqt_live_tuner.logger import logger
from .parameter_widget import ParameterWidget

class DropdownParameterWidget(ParameterWidget):
    """
    A parameter widget for selecting from a list using a QComboBox.
    Emits valueChanged(name, value) when the selection changes.
    """

    def __init__(self, name: str = "Unnamed", config: Optional[dict] = None) -> None:
        super().__init__(name, config)
        config = config or {}

        self.label = QLabel(f"{self.name}:")
        self.dropdown = QComboBox()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.dropdown)

        self.placeholder = config.get("placeholder", "Select an option")
        self.options = []
        self.value = ""

        self.update_options(config.get("options", []), config.get("initial", ""))

        # Make the dropdown editable and set placeholder text if provided
        self.dropdown.setPlaceholderText(config.get("placeholder", "Select an option"))
        self.dropdown.currentTextChanged.connect(self.on_selection_changed)

        logger.debug(f"DropdownParameterWidget created: {self.name} with options {self.options}")

    def on_selection_changed(self, text: str) -> None:
        if text == self.placeholder:
            logger.debug(f"[{self.name}] Placeholder selected, no value change emitted.")
            self.value = ""
            return

        if text != self.value:
            self.value = text
            logger.debug(f"[{self.name}] Value changed → {text}")
            self.valueChanged.emit(self.name, text)

    def set_value(self, value: str) -> None:
        if value in self.options and value != self.value:
            self.dropdown.setCurrentText(value)
            self.value = value
            logger.debug(f"[{self.name}] Value set to: {value}")
            # self.valueChanged.emit(self.name, value)

    def get_value(self) -> str:
        current_index = self.dropdown.currentIndex()
        if current_index == 0:  # Placeholder selected
            return ""
        return self.dropdown.currentText()

    def register_callback(self, callback: Callable[[str, str], None]) -> None:
        self.valueChanged.connect(callback)
        logger.debug(f"[{self.name}] Callback registered: {callback}")

    def update_options(self, options: List[str], initial: Optional[str] = None):
        """
        Update the dropdown options and optionally set a new initial value.

        Args:
            options (List[str]): The new list of options for the dropdown.
            initial (Optional[str]): The new initial value (optional).
        """
        self.options = options
        self.dropdown.clear()

        # Add placeholder as the first item
        self.dropdown.addItem(self.placeholder)
        self.dropdown.addItems(self.options)

        # Set initial value if provided and valid, otherwise select placeholder
        if not initial or initial not in self.options:
            self.dropdown.setCurrentIndex(0)  # Select placeholder
            self.value = ""  # Ensure value is empty for placeholder
        else:
            self.set_value(initial)

        logger.debug(f"[{self.name}] Options updated: {self.options}, Initial: {self.value}")
