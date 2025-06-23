import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from pyqt_live_tuner.views.parameter_widgets import FloatParameterWidget, BoolParameterWidget, DropdownParameterWidget, StringParameterWidget, ActionParameterWidget
from pyqt_live_tuner.views.parameter_groups.independent_group_widget import IndependentParameterGroup


class TestIndependentGroupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IndependentParameterGroup Test")
        self.setMinimumWidth(500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        group = IndependentParameterGroup("Independent Parameters")
        group.add_parameter(FloatParameterWidget("Gamma", {"min": 1, "max": 5, "initial": 2.2}))
        group.add_parameter(BoolParameterWidget("Enable Auto-White Balance", {"initial": False}))
        group.add_parameter(DropdownParameterWidget("White Balance Mode", {
            "options": ["Indoor", "Outdoor", "Fluorescent"],
            "initial": "Indoor"
        }))
        group.add_parameter(StringParameterWidget("Group Label", {"initial": "Independent Default"}))
        group.add_parameter(ActionParameterWidget("Reset Settings", {"label": "Reset"}))

        group.register_callback(self.handle_value_change)
        layout.addWidget(group)

    def handle_value_change(self, name, value):
        print(f"[SIGNAL] {name} changed → {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestIndependentGroupWindow()
    window.show()
    sys.exit(app.exec_())
