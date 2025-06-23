import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from pyqt_live_tuner.views.parameter_widgets.float_parameter_widget import FloatParameterWidget


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FloatParameterWidget Test")
        # self.setMinimumWidth(500)

        layout = QVBoxLayout()
        self.setLayout(layout)

        config = {
            "name": "Test Float",
            "min": 0.0,
            "max": 10.0,
            "step": 0.1,
            "initial": 5.0,
        }

        self.float_widget = FloatParameterWidget("Test Float", config)
        self.float_widget.valueChanged.connect(self.handle_value_change)

        layout.addWidget(self.float_widget)

    def handle_value_change(self, name, value):
        print(f"[SIGNAL] {name} changed → {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())
