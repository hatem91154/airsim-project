import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from pyqt_live_tuner.views.parameter_widgets import FloatParameterWidget, BoolParameterWidget, DropdownParameterWidget, StringParameterWidget, ActionParameterWidget


class TestAllParameterWidgets(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test All Parameter Widgets")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Float Parameter Widget
        float_config = {
            "min": 0.0,
            "max": 10.0,
            "step": 0.1,
            "initial": 5.0
        }
        float_widget = FloatParameterWidget("Float Parameter", float_config)
        float_widget.valueChanged.connect(self.handle_value_change)
        layout.addWidget(float_widget)

        # Bool Parameter Widget
        bool_widget = BoolParameterWidget("Boolean Parameter", {"initial": True})
        bool_widget.valueChanged.connect(self.handle_value_change)
        layout.addWidget(bool_widget)

        # Dropdown Parameter Widget
        dropdown_config = {
            "options": ["Option 1", "Option 2", "Option 3"],
            "initial": "Option 1"
        }
        dropdown_widget = DropdownParameterWidget("Dropdown Parameter", dropdown_config)
        dropdown_widget.valueChanged.connect(self.handle_value_change)
        layout.addWidget(dropdown_widget)

        # String Parameter Widget
        string_config = {
            "initial": "Default Text",
            "placeholder": "Enter text here..."
        }
        string_widget = StringParameterWidget("String Parameter", string_config)
        string_widget.valueChanged.connect(self.handle_value_change)
        layout.addWidget(string_widget)

        # Action Parameter Widget
        action_config = {
            "label": "Perform Action"
        }
        action_widget = ActionParameterWidget("Action Parameter", action_config)
        action_widget.valueChanged.connect(self.handle_value_change)
        layout.addWidget(action_widget)

    def handle_value_change(self, name, value):
        print(f"[SIGNAL] {name} changed → {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestAllParameterWidgets()
    window.show()
    sys.exit(app.exec_())
