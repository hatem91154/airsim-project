"""Configuration panel for PyQt Live Tuner.

This module provides the ConfigPanel class (formerly ConfigurationsContainer),
which serves as a container for configuration widgets and custom elements.
"""

from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget, QLabel
from typing import List, Optional


class ConfigPanel(QFrame):
    """A container for configuration widgets and custom elements.
    
    This class provides a frame that contains various configuration
    widgets and custom elements used for application-specific functionality.
    
    Attributes:
        widgets (List[QWidget]): List of widgets in the panel
        layout (QVBoxLayout): Layout for the panel's content
    """
    
    def __init__(self):
        """Initialize the configuration panel."""
        super().__init__()
        
        # Configure frame appearance
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        
        # Create layout
        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(10, 10, 10, 10)
        # self.layout.setSpacing(8)
        self.setLayout(self.layout)
        
        # Setup collection
        self.widgets: List[QWidget] = []
        
    def add_widget(self, widget: QWidget) -> None:
        """Add a widget to the panel.
        
        Args:
            widget: Widget to add
        """
        self.widgets.append(widget)
        self.layout.addWidget(widget)
        
    def add_widget_with_label(self, widget: QWidget, label_text: str) -> None:
        """Add a widget with a label above it.
        
        Args:
            widget: Widget to add
            label_text: Text for the label
        """
        label = QLabel(label_text)
        self.layout.addWidget(label)
        self.layout.addWidget(widget)
        self.widgets.append(widget)
        
    def clear(self) -> None:
        """Remove all widgets from the panel."""
        # Remove all widgets from layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Clear widget list
        self.widgets.clear()
        
    def get_widget(self, index: int) -> Optional[QWidget]:
        """Get a widget by index.
        
        Args:
            index: Index of the widget to retrieve
            
        Returns:
            The widget at the specified index, or None if index is out of range
        """
        if 0 <= index < len(self.widgets):
            return self.widgets[index]
        return None