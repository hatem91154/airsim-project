"""Parameter panel for PyQt Live Tuner.

This module provides the ParameterPanel class (formerly ParametersContainer),
which serves as a container for parameter widgets and groups.
"""

from PyQt5.QtWidgets import QScrollArea, QWidget, QVBoxLayout, QFrame
from typing import Dict, List, Any, Optional

from ..parameters.parameter import Parameter
from ..groups.parameter_group import ParameterGroup


class ParameterPanel(QScrollArea):
    """A container for parameter widgets and parameter groups.
    
    This class provides a scrollable area that contains parameter widgets
    and parameter groups, and manages their values.
    
    Attributes:
        widgets (Dict[str, Parameter]): Dictionary of parameter widgets
        groups (List[ParameterGroup]): List of parameter groups
        layout (QVBoxLayout): Layout for the panel's content
    """
    
    def __init__(self):
        """Initialize the parameter panel."""
        super().__init__()
        
        # Configure scroll area
        self.setWidgetResizable(True)
        
        # Create container widget and layout
        self.container = QWidget()
        self.layout = QVBoxLayout()
        # self.layout.setContentsMargins(10, 10, 10, 10)
        # self.layout.setSpacing(8)
        self.container.setLayout(self.layout)
        
        # Set container as scroll area widget
        self.setWidget(self.container)
        
        # Setup collections
        self.widgets: Dict[str, Parameter] = {}
        self.groups: List[ParameterGroup] = []
        
    def add_param(self, param: Parameter) -> None:
        """Add a parameter widget to the panel.
        
        Args:
            param: Parameter widget to add
        
        Note:
            If a parameter with the same name already exists, it will be replaced.
        """
        # Store the parameter
        self.widgets[param.name] = param
        
        # Create a frame for visual separation
        frame = QFrame()
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setLineWidth(1)
        
        # Add parameter to frame layout
        frame_layout = QVBoxLayout()
        # frame_layout.setContentsMargins(5, 5, 5, 5)
        frame_layout.addWidget(param)
        frame.setLayout(frame_layout)
        
        # Add frame to panel
        self.layout.addWidget(frame)
        
    def add_group(self, group: ParameterGroup) -> None:
        """Add a parameter group to the panel.
        
        Args:
            group: Parameter group to add
        """
        self.groups.append(group)
        self.layout.addWidget(group)
        
    def get_values(self) -> Dict[str, Any]:
        """Get the values of all parameters and groups.
        
        Returns:
            Dictionary of parameter and group values
        """
        values = {}
        
        # Collect individual parameter values
        for name, widget in self.widgets.items():
            values[name] = widget.get_value()
            
        # Collect parameter group values
        for group in self.groups:
            values[group.title()] = group.get_values()
            
        return values
        
    def set_values(self, values: Dict[str, Any]) -> None:
        """Set the values of parameters and groups.
        
        Args:
            values: Dictionary of parameter and group values
        """
        # Update individual parameters
        for name, value in values.items():
            if name in self.widgets:
                self.widgets[name].set_value(value)
                
        # Update parameter groups
        for group in self.groups:
            title = group.title()
            if title in values:
                group.set_values(values[title])
