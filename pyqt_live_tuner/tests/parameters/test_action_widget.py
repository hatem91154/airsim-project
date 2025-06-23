import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from pyqt_live_tuner.views.parameter_widgets.toggle_parameter_widget import ActionParameterWidget


class TestActionWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ActionParameterWidget Test")
        self.setMinimumWidth(400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        config = {
            "label": "Perform Action"
        }

        self.action_widget = ActionParameterWidget("Test Action", config)
        self.action_widget.valueChanged.connect(self.handle_value_change)

        layout.addWidget(self.action_widget)

    def handle_value_change(self, name, value):
        print(f"[SIGNAL] {name} triggered → {value}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestActionWidget()
    window.show()
    sys.exit(app.exec_())