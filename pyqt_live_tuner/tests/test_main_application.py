import sys
from PyQt5.QtWidgets import QApplication
from pyqt_live_tuner.views.main_application import MainApplication
from pyqt_live_tuner.views.containers.parameters_container import ParametersContainer
from pyqt_live_tuner.views.containers.configurations_container import ConfigurationsContainer
from pyqt_live_tuner.views.parameter_widgets import FloatParameterWidget, BoolParameterWidget
from pyqt_live_tuner.views.parameter_groups import IndependentParameterGroup


def build_parameters_container():
    container = ParametersContainer()

    # Add individual widgets
    container.add_param(FloatParameterWidget("Brightness", {"min": 0, "max": 1, "initial": 0.5}))
    container.add_param(BoolParameterWidget("Enable Shadows", {"initial": True}))

    # Add a group
    group = IndependentParameterGroup("Image Settings")
    group.add_parameter(FloatParameterWidget("Gamma", {"min": 1.0, "max": 5.0, "initial": 2.2}))
    container.add_group(group)

    return container


def build_configurations_container():
    container = ConfigurationsContainer()
    # You can add config-related widgets here if needed
    return container


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MainApplication(title="Test Main App")
    window.set_parameters_container(build_parameters_container())
    window.set_configurations_container(build_configurations_container())

    window.show()
    sys.exit(app.exec_())
