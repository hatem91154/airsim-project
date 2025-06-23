"""Base parameter class for PyQt Live Tuner.

This module provides the Parameter class (formerly ParameterWidget),
which serves as the base class for all parameter widgets in PyQt Live Tuner.
"""

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt
from typing import Any, Dict, Optional, Callable, List, Literal


class Parameter(QWidget):
    """Base class for parameter widgets in PyQt Live Tuner.
    
    This class provides common functionality for all parameter widgets,
    such as name labels, layout, and value changed signals.
    
    Attributes:
        name (str): The name of the parameter
        label (QLabel): The label widget displaying the parameter name (None if label is disabled)
        layout (QHBoxLayout or QVBoxLayout): The layout for the parameter widget
        valueChanged (pyqtSignal): Signal emitted when the parameter value changes
        
    Label Configuration:
        Labels can be configured using the config dictionary with these options:
        - show_label: Make label optional (True/False) - default: False
        - label_position: Position ('left', 'right', 'top', 'bottom') - default: 'left'
        - label_alignment: Alignment ('left', 'right', 'center') - default: 'left'
        - label_width: Minimum width in pixels - default: 100
        
    Subclasses should:
    1. Override setup_ui() to add their custom widgets to self.working_layout
    2. Implement get_value() and set_value() methods
    """
    
    valueChanged = pyqtSignal(str, object)
    
    def __init__(self, name: str = "Unnamed", config: Optional[Dict[str, Any]] = None):
        """Initialize the parameter widget.
        
        Args:
            name: The name of the parameter (default: "Unnamed")
            config: Optional configuration dictionary for parameter settings.
                   May include label options:
                   - show_label: Whether to show the label (default: False)
                   - label_position: Position of label ('left', 'right', 'top', 'bottom') (default: 'left')
                   - label_alignment: Text alignment ('left', 'right', 'center') (default: 'left')
                   - label_width: Minimum width for the label in pixels (default: 100)
        """
        super().__init__()
        
        self.name = name
        self.config = config or {}
        
        # Determine whether to show label and its position
        show_label = self.config.get('show_label', False)
        label_position = self.config.get('label_position', 'left')
        label_alignment = self.config.get('label_alignment', 'left')
        label_width = self.config.get('label_width', 30)
        
        # Create main layout based on label position
        if label_position in ('top', 'bottom'):
            self.layout = QVBoxLayout()
        else:  # 'left' or 'right'
            self.layout = QHBoxLayout()
            
        self.setLayout(self.layout)
        
        # Create content layout if needed (for top/bottom label positions)
        self.content_layout = None
        if label_position in ('top', 'bottom'):
            self.content_layout = QHBoxLayout()
            
        # Create and configure label if enabled
        self.label = None
        if show_label:
            self.label = QLabel(self.name + ":")
            self.label.setMinimumWidth(label_width)
            
            # Set alignment
            if label_alignment == 'center':
                self.label.setAlignment(Qt.AlignCenter)
            elif label_alignment == 'right':
                self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            else:  # 'left' is default
                self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
            # Add label based on position
            if label_position == 'top':
                self.layout.addWidget(self.label)
                self.layout.addLayout(self.content_layout)
            elif label_position == 'bottom':
                self.layout.addLayout(self.content_layout)
                self.layout.addWidget(self.label)
            elif label_position == 'left':
                self.layout.addWidget(self.label)
            # For 'right' position, label will be added after setup_ui()
                
        # Set the working layout (where subclasses will add their widgets)
        if self.content_layout:
            self.working_layout = self.content_layout
        else:
            self.working_layout = self.layout
            
        # Store label position and other label settings for later use
        self.label_position = label_position
        self.label_alignment = label_alignment
        self.label_width = label_width
        self.show_label = show_label
        
        # Store widgets for reconstruction during label position changes
        self.content_widgets = []
        
        # Call setup_ui for subclasses to add their widgets
        self.setup_ui()
        
        # Add the right-positioned label after setup_ui if needed
        if self.label and self.label_position == 'right':
            self.layout.addWidget(self.label)
    
    def setup_ui(self):
        """Set up the UI components for this parameter.
        
        Subclasses should override this method to add their widgets to self.working_layout.
        The base implementation does nothing.
        """
        pass
    
    def get_value(self) -> Any:
        """Get the current value of the parameter.
        
        Returns:
            The current parameter value
        """
        raise NotImplementedError("Subclasses must implement get_value()")
    
    def set_value(self, value: Any) -> None:
        """Set the value of the parameter.
        
        Args:
            value: The new value to set
        """
        raise NotImplementedError("Subclasses must implement set_value()")
    
    def register_callback(self, callback: Callable[[str, Any], None]) -> None:
        """Register a callback function to be called when the value changes.
        
        Args:
            callback: Function to be called with (name, value) when value changes
        """
        self.valueChanged.connect(callback)
        
    def set_label_position(self, position: Literal['left', 'right', 'top', 'bottom']) -> None:
        """Dynamically change the label position.
        
        Args:
            position: The new label position ('left', 'right', 'top', 'bottom')
        """
        if not self.show_label or position == self.label_position:
            return
            
        # Store all widgets currently in layouts
        self._store_content_widgets()
        
        # Clear current layouts
        self._clear_layouts()
        
        # Create new layouts based on the new position
        if position in ('top', 'bottom'):
            self.layout = QVBoxLayout()
            self.content_layout = QHBoxLayout()
        else:  # 'left' or 'right'
            self.layout = QHBoxLayout()
            self.content_layout = None
            
        self.setLayout(self.layout)
        
        # Set the working layout
        if self.content_layout:
            self.working_layout = self.content_layout
        else:
            self.working_layout = self.layout
            
        # Add label and content based on position
        if position == 'top':
            self.layout.addWidget(self.label)
            self.layout.addLayout(self.content_layout)
        elif position == 'bottom':
            self.layout.addLayout(self.content_layout)
            self.layout.addWidget(self.label)
        elif position == 'left':
            self.layout.addWidget(self.label)
        # For 'right', add content first then label
        
        # Restore all content widgets
        self._restore_content_widgets()
        
        # Add right-positioned label if needed
        if position == 'right':
            self.layout.addWidget(self.label)
            
        # Update stored label position
        self.label_position = position
        
    def set_label_alignment(self, alignment: Literal['left', 'center', 'right']) -> None:
        """Set the text alignment of the label.
        
        Args:
            alignment: The alignment for the label text ('left', 'center', 'right')
        """
        if not self.show_label:
            return
            
        if alignment == 'center':
            self.label.setAlignment(Qt.AlignCenter)
        elif alignment == 'right':
            self.label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        else:  # 'left' is default
            self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            
        self.label_alignment = alignment
        
    def _store_content_widgets(self) -> None:
        """Store all content widgets for reconstruction."""
        self.content_widgets = []
        
        # Get the layout containing content widgets
        source_layout = self.working_layout
        
        # Store all widgets
        for i in range(source_layout.count()):
            item = source_layout.itemAt(i)
            if item.widget():
                self.content_widgets.append(item.widget())
                
    def _clear_layouts(self) -> None:
        """Clear all layouts in preparation for reconstruction."""
        # Remove all widgets from layouts
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                # Don't delete the label widget, we'll reuse it
                if item.widget() != self.label:
                    item.widget().setParent(None)
            elif item.layout():
                # Clear nested layout
                while item.layout().count():
                    nested_item = item.layout().takeAt(0)
                    if nested_item.widget():
                        nested_item.widget().setParent(None)
                        
    def _restore_content_widgets(self) -> None:
        """Restore all content widgets to the working layout."""
        for widget in self.content_widgets:
            self.working_layout.addWidget(widget)