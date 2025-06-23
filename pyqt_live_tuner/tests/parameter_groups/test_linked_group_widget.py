import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from pyqt_live_tuner.views.parameter_widgets import FloatParameterWidget, BoolParameterWidget, DropdownParameterWidget, StringParameterWidget, ActionParameterWidget
from pyqt_live_tuner.views.parameter_groups.linked_group_widget import LinkedParameterGroup


class TestLinkedGroupWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("LinkedParameterGroup Test")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        group = LinkedParameterGroup("Focus Control")
        group.add_parameter(FloatParameterWidget("Focus Distance", {"min": 0.1, "max": 10.0, "step": 0.1, "initial": 2.5}))
        group.add_parameter(DropdownParameterWidget("Focus Mode", {
            "options": ["Manual", "Auto", "Continuous"], "initial": "Manual"
        }))
        group.add_parameter(BoolParameterWidget("Enable Manual Focus", {"initial": False}))
        group.add_parameter(StringParameterWidget("Focus Label", {"initial": "Default Label"}))
        group.add_parameter(ActionParameterWidget("Save Settings", {"label": "Save"}))

        group.register_callback(self.handle_group_update)
        layout.addWidget(group)

        # add another grop PID
        pid_group = LinkedParameterGroup("PID Control")
        pid_group.add_parameter(FloatParameterWidget("P Gain", {"min": 0.0, "max": 10.0, "step": 0.1, "initial": 5.0}))
        pid_group.add_parameter(FloatParameterWidget("I Gain", {"min": 0.0, "max": 10.0, "step": 0.1, "initial": 9.0}))
        pid_group.add_parameter(FloatParameterWidget("D Gain", {"min": 0.0, "max": 10.0, "step": 0.1, "initial": 1.0}))
        pid_group.register_callback(self.handle_group_update)
        layout.addWidget(pid_group)




    def handle_group_update(self, group_name, values):
        print(f"[GROUP UPDATE] {group_name} → {values}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestLinkedGroupWindow()
    window.show()
    sys.exit(app.exec_())
