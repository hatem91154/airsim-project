import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from pyqt_live_tuner.views.containers.configurations_container import ConfigurationsContainer
from pyqt_live_tuner.views.parameter_widgets import FloatParameterWidget, BoolParameterWidget, DropdownParameterWidget


class TestConfigurationsContainerWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Configurations Container")
        # self.setMinimumSize(600, 400)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Create the configurations container
        self.configurations = ConfigurationsContainer()
        layout.addWidget(self.configurations)

        # Add test widgets to the configurations container
        self.configurations.add_element(FloatParameterWidget("Test Float", {"min": 0.0, "max": 10.0, "step": 0.1, "initial": 5.0}))
        self.configurations.add_element(BoolParameterWidget("Test Bool", {"initial": True}))
        self.configurations.add_element(DropdownParameterWidget("Test Dropdown", {"options": ["Option 1", "Option 2", "Option 3"]}))

        # # Add a button to clear the configurations container
        # clear_button = QPushButton("Clear Configurations")
        # clear_button.clicked.connect(self.configurations.clear_elements)
        # layout.addWidget(clear_button)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestConfigurationsContainerWindow()
    window.show()
    sys.exit(app.exec_())