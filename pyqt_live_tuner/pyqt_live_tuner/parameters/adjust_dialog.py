from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDialogButtonBox
)
from PyQt5.QtGui import QDoubleValidator


class AdjustDialog(QDialog):
    """
    Popup dialog to adjust min, max, and step of a float parameter.
    Used in FloatParameterWidget via the ⚙ Adjust button.
    """

    def __init__(self, min_val, max_val, step, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adjust Range")

        # Line edits
        self.min_input = QLineEdit(str(min_val))
        self.max_input = QLineEdit(str(max_val))
        self.step_input = QLineEdit(str(step))

        # Apply float validation (up to 6 decimal places)
        validator = QDoubleValidator(-999999, 999999, 6)
        for field in [self.min_input, self.max_input, self.step_input]:
            field.setValidator(validator)

        # Form layout for labeled inputs
        form_layout = QFormLayout()
        form_layout.addRow("Min value:", self.min_input)
        form_layout.addRow("Max value:", self.max_input)
        form_layout.addRow("Step size:", self.step_input)

        # OK / Cancel buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        # Layout
        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(buttons)
        self.setLayout(layout)

        # Default focus
        self.min_input.setFocus()

    def get_values(self):
        """
        Returns:
            (float min, float max, float step)
        """
        return (
            float(self.min_input.text()),
            float(self.max_input.text()),
            float(self.step_input.text())
        )
