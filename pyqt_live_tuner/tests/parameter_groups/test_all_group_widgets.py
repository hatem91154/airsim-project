import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from pyqt_live_tuner.views.parameter_widgets import FloatParameterWidget, BoolParameterWidget, DropdownParameterWidget, StringParameterWidget, ActionParameterWidget
from pyqt_live_tuner.views.parameter_groups.parameter_group_widget import ParameterGroupWidget
from pyqt_live_tuner.views.parameter_groups.independent_group_widget import IndependentParameterGroup
from pyqt_live_tuner.views.parameter_groups.linked_group_widget import LinkedParameterGroup


class TestAllGroupTypesWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test All Parameter Group Types")
        self.setMinimumWidth(600)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Independent group (UI-only)
        indep_group = IndependentParameterGroup("Independent Group")
        indep_group.add_parameter(FloatParameterWidget("Gamma", {"min": 1, "max": 5, "initial": 2.2}))
        indep_group.add_parameter(BoolParameterWidget("HDR", {"initial": False}))
        indep_group.add_parameter(DropdownParameterWidget("WB Mode", {
            "options": ["Indoor", "Outdoor", "Cloudy"], "initial": "Outdoor"
        }))
        indep_group.add_parameter(StringParameterWidget("Description", {"initial": "Independent Group"}))
        indep_group.add_parameter(ActionParameterWidget("Apply Settings", {"label": "Apply"}))
        indep_group.register_callback(self.handle_independent_group_update)
        layout.addWidget(indep_group)

        # Linked group (grouped callback)
        linked_group = LinkedParameterGroup("Focus Control Group")
        linked_group.add_parameter(FloatParameterWidget("Focus Dist", {"min": 0.1, "max": 10, "initial": 2.5}))
        linked_group.add_parameter(DropdownParameterWidget("Focus Mode", {
            "options": ["Manual", "Auto", "Continuous"], "initial": "Auto"
        }))
        linked_group.add_parameter(BoolParameterWidget("Enable Manual", {"initial": True}))
        linked_group.add_parameter(StringParameterWidget("Focus Label", {"initial": "Focus Default"}))
        linked_group.add_parameter(ActionParameterWidget("Save Focus", {"label": "Save"}))
        linked_group.register_callback(self.handle_linked_group_update)
        layout.addWidget(linked_group)

    def handle_independent_group_update(self, name, value):
        print(f"[INDEPENDENT GROUP] {name} changed → {value}")

    def handle_linked_group_update(self, group_name, values):
        print(f"[GROUP UPDATE] {group_name} → {values}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestAllGroupTypesWindow()
    window.show()
    sys.exit(app.exec_())
