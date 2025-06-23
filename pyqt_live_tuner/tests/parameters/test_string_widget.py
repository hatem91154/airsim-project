import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from pyqt_live_tuner.views.parameter_widgets.string_parameter_widget import StringParameterWidget


class TestStringWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StringParameterWidget Test")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        config = {
            "initial": "Default Text",
            "placeholder": "Enter text here..."
        }

        self.string_widget = StringParameterWidget("Test String", config)
        self.string_widget.valueChanged.connect(self.handle_value_change)

        layout.addWidget(self.string_widget)

    def handle_value_change(self, name, value):
        print(f"[SIGNAL] {name} changed → {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestStringWidget()
    window.show()
    sys.exit(app.exec_())