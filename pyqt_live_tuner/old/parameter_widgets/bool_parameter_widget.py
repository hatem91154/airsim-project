from PyQt5.QtWidgets import QLabel, QCheckBox

from pyqt_live_tuner.logger import logger
from .parameter_widget import ParameterWidget

class BoolParameterWidget(ParameterWidget):
    """
    A parameter widget for boolean values using a QCheckBox.
    Emits valueChanged(name, value) when toggled.
    """

    def __init__(self, name: str = "Unnamed", config: dict = None):
        super().__init__(name, config)
        config = config or {}

        self.value = config.get("initial", False)

        self.label = QLabel(f"{self.name}:")
        self.checkbox = QCheckBox()
        self.checkbox.setChecked(self.value)

        self.checkbox.stateChanged.connect(self.on_toggle)

        # Use inherited layout
        layout = self.layout
        layout.addWidget(self.label)
        layout.addWidget(self.checkbox)

        logger.debug(f"BoolParameterWidget created: {self.name} = {self.value}")

    def on_toggle(self, state: int):
        checked = bool(state)
        if checked != self.value:
            self.value = checked
            logger.debug(f"[{self.name}] Value changed → {self.value}")
            self.valueChanged.emit(self.name, self.value)

    def set_value(self, value: bool):
        if bool(value) != self.value:
            self.value = bool(value)
            self.checkbox.setChecked(self.value)
            logger.debug(f"[{self.name}] Value set to: {self.value}")
            self.valueChanged.emit(self.name, self.value)

    def get_value(self) -> bool:
        logger.debug(f"[{self.name}] Value retrieved: {self.value}")
        return self.value

    def register_callback(self, callback):
        """
        Register a callback function to be called when the value changes.
        The callback should accept two arguments: name and value.
        """
        self.valueChanged.connect(callback)
        logger.debug(f"[{self.name}] Callback registered.")
