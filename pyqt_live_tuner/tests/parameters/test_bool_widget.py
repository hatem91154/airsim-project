import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from pyqt_live_tuner.views.parameter_widgets.bool_parameter_widget import BoolParameterWidget


class TestBoolWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BoolParameterWidget Test")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.bool_widget = BoolParameterWidget("Enable Feature")
        self.bool_widget.register_callback(self.handle_value_change)

        layout.addWidget(self.bool_widget)

    def handle_value_change(self, name, value):
        print(f"[SIGNAL] {name} changed → {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestBoolWindow()
    window.show()
    sys.exit(app.exec_())
