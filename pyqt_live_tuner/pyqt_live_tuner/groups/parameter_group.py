"""Parameter group base class for PyQt Live Tuner.

This module provides the ParameterGroup base class (formerly ParameterGroupWidget),
which serves as the base class for all parameter group widgets.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QGroupBox
from typing import Dict, Any, List, Optional

from ..parameters.parameter import Parameter
from PyQt5.QtWidgets import QHBoxLayout

from typing import Any, Dict, Optional, Callable, List, Literal

class BaseParameterGroup(QGroupBox):
    """Base class for parameter groups in PyQt Live Tuner.
    
    This class provides a container for grouping related parameters
    together under a collapsible group box.
    
    Attributes:
        _name (str): The name/title of the group
        layout (QVBoxLayout): The layout for the group's content
    """
    
    def __init__(self, name: str = "Unnamed Group", config: Optional[Dict[str, Any]] = None):
        """Initialize the parameter group.
        
        Args:
            name: The name/title of the group (default: "Unnamed Group")
        """
        super().__init__(name)
        
        self._name = name
        
        # Determine layout type based on config
        if config and config.get("layout") == "vertical":
            self.layout = QVBoxLayout()
        else:
            self.layout = QHBoxLayout()
        
        # Set layout properties
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)
        
        def title(self) -> str:
            """Get the title of the parameter group.
            
            Returns:
                The title of the group
            """
        return self._name
        
    def get_values(self) -> Dict[str, Any]:
        """Get the values of all parameters in the group.
        
        Returns:
            Dictionary of parameter values
        """
        raise NotImplementedError("Subclasses must implement get_values()")
        
    def set_values(self, values: Dict[str, Any]) -> None:
        """Set the values of parameters in the group.
        
        Args:
            values: Dictionary of parameter values
        """
        raise NotImplementedError("Subclasses must implement set_values()")
        
    def add_parameter(self, param: Parameter) -> None:
        """Add a parameter to the group.
        
        Args:
            param: Parameter to add
        """
        raise NotImplementedError("Subclasses must implement add_parameter()")
        

class ParameterGroup(BaseParameterGroup):
    """A group of related parameters in PyQt Live Tuner.
    
    This class provides a container for grouping related parameters
    together under a collapsible group box.
    
    Attributes:
        _parameters (Dict[str, Parameter]): Dictionary mapping parameter names to Parameter objects
    """
    
    def __init__(self, name: str = "Unnamed Group"):
        """Initialize the parameter group.
        
        Args:
            name: The name/title of the group (default: "Unnamed Group")
        """
        super().__init__(name)
        self._parameters: Dict[str, Parameter] = {}
    
    def add_parameter(self, param: Parameter) -> None:
        """Add a parameter to the group.
        
        Args:
            param: Parameter to add
        """
        self._parameters[param.name] = param
        self.layout.addWidget(param)

    def add_parameters(self, params: List[Parameter]) -> None:
        """Add multiple parameters to the group.
        
        Args:
            params: List of parameters to add
        """
        for param in params:
            self.add_parameter(param)

    def get_values(self) -> Dict[str, Any]:
        """Get the values of all parameters in the group.
        
        Returns:
            Dictionary of parameter values
        """
        values = {}
        for name, param in self._parameters.items():
            values[name] = param.get_value()
        return values

    def set_values(self, values: Dict[str, Any]) -> None:
        """Set the values of parameters in the group.
        
        Args:
            values: Dictionary of parameter values
        """
        for name, value in values.items():
            if name in self._parameters:
                self._parameters[name].set_value(value)
        else:
            raise ValueError(f"Parameter '{name}' not found in group '{self._name}'")
        
