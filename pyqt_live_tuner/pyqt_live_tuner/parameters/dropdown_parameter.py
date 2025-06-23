"""Dropdown parameter class for PyQt Live Tuner.

This module provides the DropdownParameter class (formerly DropdownParameterWidget),
which implements a dropdown selection parameter widget.
"""

from typing import List, Dict, Any, Optional

from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt

from .parameter import Parameter


class DropdownParameter(Parameter):
    """A parameter widget that provides a dropdown selection.
    
    This class allows users to select from a predefined list of options
    using a dropdown menu (QComboBox).
    
    Attributes:
        options (List[str]): Available options in the dropdown
        dropdown (QComboBox): The dropdown widget
        placeholder (str): Placeholder text when no option is selected
        value (str): The currently selected option
    """
    
    def __init__(self, name: str = "Unnamed", config: Optional[Dict[str, Any]] = None):
        """Initialize the dropdown parameter.
        
        Args:
            name: The name of the parameter (default: "Unnamed")
            config: Configuration dictionary, which may include:
                options (List[str]): Available options
                initial (str): Initial selected option
                placeholder (str): Placeholder text
        """
        super().__init__(name, config)
        
        # Setup configuration
        self.options = self.config.get("options", [])
        self.placeholder = self.config.get("placeholder", "Select an option")
        
        # Create dropdown widget
        self.dropdown = QComboBox()
        self.dropdown.setEditable(False)
        self.dropdown.setPlaceholderText(self.placeholder)
        self.layout.addWidget(self.dropdown)
        
        # Add placeholder and options
        self.dropdown.addItem(self.placeholder)
        for option in self.options:
            self.dropdown.addItem(option)
        
        # Set initial value
        self.value = ""
        if "initial" in self.config and self.config["initial"] in self.options:
            self.set_value(self.config["initial"])
            
        # Connect signals
        self.dropdown.currentTextChanged.connect(self.on_selection_changed)
    
    def on_selection_changed(self, text: str) -> None:
        """Handle changes in the dropdown selection.
        
        Args:
            text: The newly selected text
        """
        if text == self.placeholder:
            self.value = ""
            return
            
        self.value = text
        self.valueChanged.emit(self.name, self.value)
    
    def get_value(self) -> str:
        """Get the current value of the parameter.
        
        Returns:
            The currently selected option, or empty string if none selected
        """
        if self.dropdown.currentText() == self.placeholder:
            return ""
        return self.dropdown.currentText()
    
    def set_value(self, value: str) -> None:
        """Set the value of the parameter.
        
        Args:
            value: The option to select
        
        Note:
            If the value is not in the options list, no change will occur
        """
        if value == self.value:
            return
            
        found = False
        for i in range(self.dropdown.count()):
            if self.dropdown.itemText(i) == value:
                self.dropdown.setCurrentIndex(i)
                self.value = value
                found = True
                break
                
        if not found and value in self.options:
            # Option exists but might not be in dropdown yet
            self.dropdown.addItem(value)
            self.dropdown.setCurrentText(value)
            self.value = value
    
    def update_options(self, options: List[str], initial: Optional[str] = None) -> None:
        """Update the available options in the dropdown.
        
        Args:
            options: New list of available options
            initial: Optional initial value to set after updating options
        """
        # Save current selection
        current = self.value
        
        # Update options list
        self.options = options
        
        # Clear and repopulate dropdown
        self.dropdown.clear()
        self.dropdown.addItem(self.placeholder)
        for option in self.options:
            self.dropdown.addItem(option)
            
        # Set initial value or restore previous value if it's still valid
        if initial is not None and initial in self.options:
            self.set_value(initial)
        elif current in self.options:
            self.set_value(current)
        else:
            self.dropdown.setCurrentIndex(0)  # Select placeholder
            self.value = ""