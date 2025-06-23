"""
Industrial-level test suite for the DropdownParameterWidget class.

This module tests the functionality of the DropdownParameterWidget class,
which provides a dropdown selection widget for parameter tuning.
"""
import pytest
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from pyqt_live_tuner.parameter_widgets.dropdown_parameter_widget import DropdownParameterWidget


class TestDropdownParameterWidget:
    """Comprehensive test suite for DropdownParameterWidget class."""

    def test_initialization_default_params(self, qapp):
        """
        Test initialization with default parameters.
        
        Verifies:
        - Widget is properly initialized with default parameters
        - QComboBox is created with default properties
        - Default placeholder text is set
        - No options are added by default
        """
        # Act
        widget = DropdownParameterWidget()
        
        # Assert
        assert widget.name == "Unnamed"
        assert widget.dropdown is not None
        assert isinstance(widget.dropdown, QComboBox)
        assert widget.placeholder == "Select an option"
        assert widget.value == ""
        assert len(widget.options) == 0
        assert widget.dropdown.currentText() == widget.placeholder
        assert widget.dropdown.count() == 1  # Should have placeholder

    def test_initialization_with_name(self, qapp):
        """
        Test initialization with a custom name.
        
        Verifies:
        - Widget name is set correctly
        - Label displays the correct name
        """
        # Act
        widget = DropdownParameterWidget("Custom Name")
        
        # Assert
        assert widget.name == "Custom Name"
        assert "Custom Name" in widget.label.text()

    def test_initialization_with_options(self, qapp):
        """
        Test initialization with options.
        
        Verifies:
        - Options are added to the dropdown
        - Dropdown count matches options count plus placeholder
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        
        # Act
        widget = DropdownParameterWidget("Test", {"options": options})
        
        # Assert
        assert widget.options == options
        assert widget.dropdown.count() == len(options) + 1  # +1 for placeholder
        
        # Check each option is in the dropdown
        for i, option in enumerate(options):
            assert widget.dropdown.itemText(i + 1) == option  # +1 to skip placeholder

    def test_initialization_with_initial_value(self, qapp):
        """
        Test initialization with an initial value.
        
        Verifies:
        - Initial value is set correctly
        - Dropdown selection matches initial value
        - Value property matches initial value
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        initial = "Option 2"
        
        # Act
        widget = DropdownParameterWidget("Test", {
            "options": options,
            "initial": initial
        })
        
        # Assert
        assert widget.value == initial
        assert widget.dropdown.currentText() == initial

    def test_initialization_with_custom_placeholder(self, qapp):
        """
        Test initialization with a custom placeholder.
        
        Verifies:
        - Custom placeholder is set correctly
        - Dropdown placeholder text is updated
        """
        # Arrange
        custom_placeholder = "Select something..."
        
        # Act
        widget = DropdownParameterWidget("Test", {
            "placeholder": custom_placeholder
        })
        
        # Assert
        assert widget.placeholder == custom_placeholder
        assert widget.dropdown.placeholderText() == custom_placeholder

    def test_signal_connection(self, qapp):
        """
        Test that the signal connection is properly set up.
        
        Verifies:
        - currentTextChanged signal is connected to on_selection_changed
        """
        # Arrange
        widget = DropdownParameterWidget()
        widget.on_selection_changed = MagicMock()
        
        # Act - simulate signal emission
        widget.dropdown.setCurrentIndex(0)  # Select the placeholder
        widget.dropdown.currentTextChanged.emit(widget.placeholder)
        
        # Assert
        widget.on_selection_changed.assert_called_once_with(widget.placeholder)

    def test_on_selection_changed_to_valid_value(self, qapp):
        """
        Test on_selection_changed with a valid value.
        
        Verifies:
        - Value is updated
        - valueChanged signal is emitted with correct parameters
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options})
        
        # Mock the valueChanged signal
        widget.valueChanged = MagicMock()
        
        # Act
        widget.on_selection_changed("Option 2")
        
        # Assert
        assert widget.value == "Option 2"
        widget.valueChanged.emit.assert_called_once_with("Test", "Option 2")

    def test_on_selection_changed_to_placeholder(self, qapp):
        """
        Test on_selection_changed with the placeholder value.
        
        Verifies:
        - Value is set to empty string
        - valueChanged signal is not emitted
        """
        # Arrange
        widget = DropdownParameterWidget()
        widget.value = "Some value"  # Set an initial value
        
        # Mock the valueChanged signal
        widget.valueChanged = MagicMock()
        
        # Act
        widget.on_selection_changed(widget.placeholder)
        
        # Assert
        assert widget.value == ""
        widget.valueChanged.emit.assert_not_called()

    def test_on_selection_changed_to_same_value(self, qapp):
        """
        Test on_selection_changed with the same value.
        
        Verifies:
        - Value remains unchanged
        - valueChanged signal is still emitted
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options, "initial": "Option 2"})
        
        # Mock the valueChanged signal
        widget.valueChanged = MagicMock()
        
        # Act
        widget.on_selection_changed("Option 2")
        
        # Assert
        assert widget.value == "Option 2"
        widget.valueChanged.emit.assert_called_once()

    def test_set_value_valid(self, qapp):
        """
        Test set_value with a valid value.
        
        Verifies:
        - Value is updated
        - Dropdown selection is updated
        - valueChanged signal is not emitted
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options})
        
        # Mock the valueChanged signal
        widget.valueChanged = MagicMock()
        
        # Act
        widget.set_value("Option 3")
        
        # Assert
        assert widget.value == "Option 3"
        assert widget.dropdown.currentText() == "Option 3"
        widget.valueChanged.emit.assert_not_called()

    def test_set_value_invalid(self, qapp):
        """
        Test set_value with an invalid value.
        
        Verifies:
        - Value is not updated
        - Dropdown selection is not changed
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options, "initial": "Option 2"})
        
        # Act
        widget.set_value("Invalid Option")
        
        # Assert
        assert widget.value == "Option 2"  # Value remains unchanged
        assert widget.dropdown.currentText() == "Option 2"  # Dropdown remains unchanged

    def test_set_value_same_value(self, qapp):
        """
        Test set_value with the same value.
        
        Verifies:
        - No change is made
        - valueChanged signal is not emitted
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options, "initial": "Option 2"})
        
        # Mock the valueChanged signal
        widget.valueChanged = MagicMock()
        
        # Act
        widget.set_value("Option 2")
        
        # Assert
        assert widget.value == "Option 2"
        widget.valueChanged.emit.assert_not_called()

    def test_get_value(self, qapp):
        """
        Test get_value method.
        
        Verifies:
        - Returns the current value correctly
        - Returns empty string when placeholder is selected
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options})
        
        # Act - Test with placeholder selected
        widget.dropdown.setCurrentIndex(0)  # Select placeholder
        placeholder_value = widget.get_value()
        
        # Act - Test with a valid option selected
        widget.dropdown.setCurrentIndex(2)  # Select "Option 2"
        option_value = widget.get_value()
        
        # Assert
        assert placeholder_value == ""
        assert option_value == "Option 2"

    def test_register_callback(self, qapp):
        """
        Test register_callback method.
        
        Verifies:
        - Callback function is connected to valueChanged signal
        """
        # Arrange
        widget = DropdownParameterWidget()
        callback = MagicMock()
        
        # Act
        widget.register_callback(callback)
        widget.valueChanged.emit("Test", "Value")
        
        # Assert
        callback.assert_called_once_with("Test", "Value")

    def test_update_options_empty(self, qapp):
        """
        Test updating options with an empty list.
        
        Verifies:
        - Options are cleared
        - Dropdown only contains placeholder
        - Value is reset to empty string
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options, "initial": "Option 2"})
        
        # Act
        widget.update_options([])
        
        # Assert
        assert widget.options == []
        assert widget.dropdown.count() == 1  # Only placeholder
        assert widget.value == ""
        assert widget.dropdown.currentIndex() == 0  # Placeholder selected

    def test_update_options_with_valid_initial(self, qapp):
        """
        Test updating options with a valid initial value.
        
        Verifies:
        - Options are updated
        - Dropdown contains all options
        - Initial value is selected
        """
        # Arrange
        widget = DropdownParameterWidget("Test")
        new_options = ["New 1", "New 2", "New 3"]
        
        # Act
        widget.update_options(new_options, "New 2")
        
        # Assert
        assert widget.options == new_options
        assert widget.dropdown.count() == len(new_options) + 1  # +1 for placeholder
        assert widget.value == "New 2"
        assert widget.dropdown.currentText() == "New 2"

    def test_update_options_with_invalid_initial(self, qapp):
        """
        Test updating options with an invalid initial value.
        
        Verifies:
        - Options are updated
        - Dropdown contains all options
        - Placeholder is selected
        - Value is reset to empty string
        """
        # Arrange
        widget = DropdownParameterWidget("Test", {"initial": "Old Value"})
        new_options = ["New 1", "New 2", "New 3"]
        
        # Act
        widget.update_options(new_options, "Invalid")
        
        # Assert
        assert widget.options == new_options
        assert widget.dropdown.count() == len(new_options) + 1  # +1 for placeholder
        assert widget.value == ""
        assert widget.dropdown.currentIndex() == 0  # Placeholder selected

    def test_update_options_no_initial(self, qapp):
        """
        Test updating options without specifying an initial value.
        
        Verifies:
        - Options are updated
        - Dropdown contains all options
        - Placeholder is selected
        - Value is reset to empty string
        """
        # Arrange
        widget = DropdownParameterWidget("Test", {"initial": "Old Value"})
        new_options = ["New 1", "New 2", "New 3"]
        
        # Act
        widget.update_options(new_options)
        
        # Assert
        assert widget.options == new_options
        assert widget.dropdown.count() == len(new_options) + 1  # +1 for placeholder
        assert widget.value == ""
        assert widget.dropdown.currentIndex() == 0  # Placeholder selected

    def test_integration_user_interaction(self, qtbot_extended):
        """
        Integration test for user interaction with the dropdown.
        
        Verifies:
        - User can select options from the dropdown
        - Changing selection updates the value
        - valueChanged signal is emitted with correct parameters
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options})
        qtbot_extended.addWidget(widget)
        
        # Mock the callback function
        callback = MagicMock()
        widget.register_callback(callback)
        
        # Act - Simulate user clicking the dropdown and selecting an option
        qtbot_extended.mouseClick(widget.dropdown, Qt.LeftButton)
        
        # This is a bit tricky to test programmatically, so we'll directly set the index
        widget.dropdown.setCurrentIndex(2)  # Select "Option 2"
        
        # Assert
        assert widget.value == "Option 2"
        callback.assert_called_with("Test", "Option 2")

    def test_integration_signal_emission(self, qtbot_extended):
        """
        Integration test for signal emission.
        
        Verifies:
        - Signals are properly emitted when selection changes
        - Signals contain the correct parameters
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = DropdownParameterWidget("Test", {"options": options})
        qtbot_extended.addWidget(widget)
        
        # Use qtbot to spy on the signal
        with qtbot_extended.waitSignal(widget.valueChanged, timeout=1000) as blocker:
            # Act - Change the selection
            widget.dropdown.setCurrentIndex(2)  # Select "Option 2"
        
        # Assert
        assert blocker.args == ["Test", "Option 2"]
        assert widget.value == "Option 2"