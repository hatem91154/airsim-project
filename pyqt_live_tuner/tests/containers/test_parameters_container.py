import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from pyqt_live_tuner.views.containers.parameters_container import ParametersContainer
from pyqt_live_tuner.views.parameter_widgets import FloatParameterWidget, BoolParameterWidget, DropdownParameterWidget
from pyqt_live_tuner.views.parameter_groups import IndependentParameterGroup, LinkedParameterGroup


class TestContainerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test ParametersContainer")
        # self.setMinimumSize(700, 600)

        self.container = ParametersContainer()
        self.setCentralWidget(self.container)

        # Add individual parameter widgets
        self.container.add_param(FloatParameterWidget("Brightness", {"min": 0, "max": 1, "step": 0.01, "initial": 0.5}))
        self.container.add_param(BoolParameterWidget("Enable Shadows", {"initial": True}))

        # Add an independent group
        indep_group = IndependentParameterGroup("Image Settings")
        indep_group.add_parameter(FloatParameterWidget("Gamma", {"min": 1.0, "max": 5.0, "initial": 2.2}))
        indep_group.add_parameter(DropdownParameterWidget("Color Profile", {
            "options": ["sRGB", "Rec709", "DCI-P3"], "initial": "sRGB"
        }))
        self.container.add_group(indep_group)

        # Add a linked group
        linked_group = LinkedParameterGroup("Lens Settings")
        linked_group.add_parameter(FloatParameterWidget("Focus Distance", {"min": 0.1, "max": 10.0, "initial": 3.0}))
        linked_group.add_parameter(BoolParameterWidget("Enable Manual Focus", {"initial": False}))
        linked_group.register_callback(self.handle_group_change)
        self.container.add_group(linked_group)

    def handle_group_change(self, group_name, values):
        print(f"[GROUP UPDATED] {group_name} → {values}")


if __name__ == "__main__":
    import qdarkstyle

    app = QApplication(sys.argv)

    # import qdarktheme
    # app.setStyleSheet(qdarktheme.load_stylesheet("dark"))  # or "light"

    window = TestContainerWindow()
    window.show()
    sys.exit(app.exec_())