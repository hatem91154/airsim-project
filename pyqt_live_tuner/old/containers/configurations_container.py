from PyQt5.QtWidgets import QFrame, QVBoxLayout


class ConfigurationsContainer(QFrame):
    """
    A footer container for dynamically adding user-defined parameter widgets or custom elements.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

    def add_element(self, widget):
        """
        Add a custom widget or parameter widget to the footer container.

        Args:
            widget (QWidget): The widget to add.
        """
        self.layout.addWidget(widget)
