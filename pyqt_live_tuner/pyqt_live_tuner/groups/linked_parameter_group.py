"""Linked parameter group for PyQt Live Tuner.

This module provides the LinkedParameterGroup class, which manages a group of 
parameters that are linked together and emit a signal when any parameter changes.
"""

from PyQt5.QtCore import pyqtSignal
from typing import Callable, Dict, Any

from .parameter_group import BaseParameterGroup
from ..parameters.parameter import Parameter

from typing import Any, Dict, Optional, Callable, List, Literal


class LinkedParameterGroup(BaseParameterGroup):
    """A group of related parameters that are linked together.
    
    When any parameter in this group changes, a groupChanged signal is emitted
    with the group name and a dictionary of all parameter values.
    
    Attributes:
        groupChanged: Signal emitted when any parameter changes
        _parameters: Dictionary mapping parameter names to Parameter objects
    """
    
    groupChanged = pyqtSignal(str, dict)
    
    def __init__(self, name: str = "Linked Group", config: Optional[Dict[str, Any]] = None):
        """Initialize the linked parameter group.
        
        Args:
            name: The name/title of the group (default: "Linked Group")
            config: Configuration dictionary for the group
        """
        super().__init__(name, config)
        self._parameters = {}
        
    def add_parameter(self, param: Parameter) -> None:
        """Add a parameter to the group and connect its signals.
        
        Args:
            param: Parameter to add
        """
        self._parameters[param.name] = param
        self.layout.addWidget(param)
        
        # Connect the parameter's valueChanged signal to our handler
        param.valueChanged.connect(self._on_any_value_changed)

    def add_parameters(self, params: List[Parameter]) -> None:
        """Add multiple parameters to the group.
        
        Args:
            params: List of parameters to add
        """
        for param in params:
            self.add_parameter(param)

    def _on_any_value_changed(self, *_):
        """Handle when any parameter in the group changes.
        
        Emits the groupChanged signal with the group name and current values.
        """
        self.groupChanged.emit(self.title(), self.get_values())
        
    def get_values(self) -> Dict[str, Any]:
        """Get the values of all parameters in the group.
        
        Returns:
            Dictionary of parameter values
        """
        return {name: param.get_value() for name, param in self._parameters.items()}
        
    def set_values(self, values: Dict[str, Any]) -> None:
        """Set the values of parameters in the group.
        
        Args:
            values: Dictionary of parameter values
        """
        for name, value in values.items():
            if name in self._parameters:
                self._parameters[name].set_value(value)
                
    def register_callback(self, callback: Callable[[str, dict], None]) -> None:
        """Register a function to handle group-level changes.
        
        Args:
            callback: Function that takes (group_name: str, values: dict)
        """
        self.groupChanged.connect(callback)
        
    def get_parameter(self, name: str) -> Parameter:
        """Get a parameter by name.
        
        Args:
            name: Name of the parameter to retrieve
            
        Returns:
            The parameter object
            
        Raises:
            KeyError: If parameter with the given name doesn't exist
        """
        if name in self._parameters:
            return self._parameters[name]
        raise KeyError(f"Parameter '{name}' not found in this group")