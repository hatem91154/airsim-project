import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton
from pyqt_live_tuner.views.parameter_widgets.dropdown_parameter_widget import DropdownParameterWidget


class TestDropdownWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DropdownParameterWidget Test")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # config = {
        #     "name": "Test Dropdown",
        #     "options": ["Option A", "Option B", "Option C", "Option D"]
        # }

        self.dropdown_widget = DropdownParameterWidget("Test Dropdown", {
            "options": ["Option A", "Option B", "Option C", "Option D"]        })
        self.dropdown_widget.register_callback(self.handle_value_change)
        layout.addWidget(self.dropdown_widget)

        # Add a button to update options dynamically
        update_button = QPushButton("Update Options")
        update_button.clicked.connect(self.update_dropdown_options)
        layout.addWidget(update_button)

    def handle_value_change(self, name, value):
        print(f"[SIGNAL] {name} changed → {value}")

    def update_dropdown_options(self):
        """Update the dropdown options dynamically."""
        new_options = ["New Option 1", "New Option 2", "New Option 3"]
        self.dropdown_widget.update_options(new_options)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestDropdownWindow()
    window.show()
    sys.exit(app.exec_())
