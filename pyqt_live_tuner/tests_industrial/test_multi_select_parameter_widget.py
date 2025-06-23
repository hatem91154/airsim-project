"""
Industrial-level test suite for the MultiSelectParameterWidget class.

This module tests the functionality of the MultiSelectParameterWidget class,
which provides a widget for selecting multiple options from a list.
"""
import pytest
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from pyqt_live_tuner.parameter_widgets.multi_select_parameter_widget import MultiSelectParameterWidget


class TestMultiSelectParameterWidget:
    """Comprehensive test suite for MultiSelectParameterWidget class."""

    def test_initialization_default_params(self, qapp):
        """
        Test initialization with default parameters.
        
        Verifies:
        - Widget is properly initialized with default parameters
        - QListWidget is created with default properties
        - No options are added by default
        - Selection mode is set to MultiSelection
        """
        # Act
        widget = MultiSelectParameterWidget()
        
        # Assert
        assert widget.name == "Unnamed"
        assert widget.list_widget is not None
        assert isinstance(widget.list_widget, QListWidget)
        assert widget.list_widget.count() == 0
        assert widget.value == []
        assert len(widget.options) == 0
        assert widget.list_widget.selectionMode() == QListWidget.MultiSelection

    def test_initialization_with_name(self, qapp):
        """
        Test initialization with a custom name.
        
        Verifies:
        - Widget name is set correctly
        - Label displays the correct name
        """
        # Act
        widget = MultiSelectParameterWidget("Custom Name")
        
        # Assert
        assert widget.name == "Custom Name"
        assert "Custom Name" in widget.label.text()

    def test_initialization_with_options(self, qapp):
        """
        Test initialization with options.
        
        Verifies:
        - Options are added to the list widget
        - List widget count matches options count
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        
        # Act
        widget = MultiSelectParameterWidget("Test", {"options": options})
        
        # Assert
        assert widget.options == options
        assert widget.list_widget.count() == len(options)
        
        # Check each option is in the list widget
        for i, option in enumerate(options):
            assert widget.list_widget.item(i).text() == option

    def test_initialization_with_initial_values(self, qapp):
        """
        Test initialization with initial values.
        
        Verifies:
        - Initial values are selected correctly
        - Value property matches initial values
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        initial = ["Option 1", "Option 3"]
        
        # Act
        widget = MultiSelectParameterWidget("Test", {
            "options": options,
            "initial": initial
        })
        
        # Assert
        assert sorted(widget.value) == sorted(initial)
        
        # Check that the correct items are selected
        for i in range(widget.list_widget.count()):
            item = widget.list_widget.item(i)
            if item.text() in initial:
                assert item.isSelected()
            else:
                assert not item.isSelected()

    def test_initialization_with_height(self, qapp):
        """
        Test initialization with custom height.
        
        Verifies:
        - List widget height is set correctly
        """
        # Arrange
        custom_height = 150
        
        # Act
        widget = MultiSelectParameterWidget("Test", {
            "height": custom_height
        })
        
        # Assert
        assert widget.list_widget.minimumHeight() == custom_height

    def test_signal_connection(self, qapp):
        """
        Test that the signal connection is properly set up.
        
        Verifies:
        - itemSelectionChanged signal is connected to on_selection_changed
        """
        # Arrange
        widget = MultiSelectParameterWidget()
        widget.on_selection_changed = MagicMock()
        
        # Act - simulate signal emission
        widget.list_widget.itemSelectionChanged.emit()
        
        # Assert
        widget.on_selection_changed.assert_called_once()

    def test_on_selection_changed(self, qapp):
        """
        Test on_selection_changed method.
        
        Verifies:
        - Value is updated correctly
        - valueChanged signal is emitted with correct parameters
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        widget = MultiSelectParameterWidget("Test", {"options": options})
        
        # Mock the valueChanged signal
        widget.valueChanged = MagicMock()
        
        # Select some items
        widget.list_widget.item(0).setSelected(True)
        widget.list_widget.item(2).setSelected(True)
        
        # Act
        widget.on_selection_changed()
        
        # Assert
        assert sorted(widget.value) == ["Option 1", "Option 3"]
        widget.valueChanged.emit.assert_called_once_with("Test", ["Option 1", "Option 3"])

    def test_set_value_valid(self, qapp):
        """
        Test set_value with valid values.
        
        Verifies:
        - Value is updated correctly
        - List widget selections are updated
        - valueChanged signal is not emitted
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        widget = MultiSelectParameterWidget("Test", {"options": options})
        
        # Mock the valueChanged signal
        widget.valueChanged = MagicMock()
        
        # Act
        widget.set_value(["Option 2", "Option 4"])
        
        # Assert
        assert sorted(widget.value) == ["Option 2", "Option 4"]
        
        # Check that the correct items are selected
        for i in range(widget.list_widget.count()):
            item = widget.list_widget.item(i)
            if item.text() in ["Option 2", "Option 4"]:
                assert item.isSelected()
            else:
                assert not item.isSelected()
                
        # Signal should not be emitted
        widget.valueChanged.emit.assert_not_called()

    def test_set_value_invalid(self, qapp):
        """
        Test set_value with invalid values.
        
        Verifies:
        - Invalid options are ignored
        - Valid options are still selected
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        widget = MultiSelectParameterWidget("Test", {"options": options})
        
        # Act
        widget.set_value(["Option 2", "Invalid Option", "Option 3"])
        
        # Assert
        assert sorted(widget.value) == ["Option 2", "Option 3"]
        
        # Check that only valid items are selected
        for i in range(widget.list_widget.count()):
            item = widget.list_widget.item(i)
            if item.text() in ["Option 2", "Option 3"]:
                assert item.isSelected()
            else:
                assert not item.isSelected()

    def test_set_value_empty_list(self, qapp):
        """
        Test set_value with an empty list.
        
        Verifies:
        - All selections are cleared
        - Value is set to empty list
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = MultiSelectParameterWidget("Test", {
            "options": options,
            "initial": ["Option 1", "Option 3"]
        })
        
        # Act
        widget.set_value([])
        
        # Assert
        assert widget.value == []
        
        # Check that no items are selected
        for i in range(widget.list_widget.count()):
            assert not widget.list_widget.item(i).isSelected()

    def test_get_value(self, qapp):
        """
        Test get_value method.
        
        Verifies:
        - Returns the current selections correctly
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        selected = ["Option 1", "Option 3"]
        widget = MultiSelectParameterWidget("Test", {
            "options": options,
            "initial": selected
        })
        
        # Act
        value = widget.get_value()
        
        # Assert
        assert sorted(value) == sorted(selected)

    def test_register_callback(self, qapp):
        """
        Test register_callback method.
        
        Verifies:
        - Callback function is connected to valueChanged signal
        """
        # Arrange
        widget = MultiSelectParameterWidget()
        callback = MagicMock()
        
        # Act
        widget.register_callback(callback)
        widget.valueChanged.emit("Test", ["Value1", "Value2"])
        
        # Assert
        callback.assert_called_once_with("Test", ["Value1", "Value2"])

    def test_update_options_empty(self, qapp):
        """
        Test updating options with an empty list.
        
        Verifies:
        - Options are cleared
        - List widget is emptied
        - Value is reset to empty list
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3"]
        widget = MultiSelectParameterWidget("Test", {
            "options": options,
            "initial": ["Option 1"]
        })
        
        # Act
        widget.update_options([])
        
        # Assert
        assert widget.options == []
        assert widget.list_widget.count() == 0
        assert widget.value == []

    def test_update_options_with_valid_initial(self, qapp):
        """
        Test updating options with valid initial values.
        
        Verifies:
        - Options are updated
        - List widget contains all options
        - Initial values are selected
        """
        # Arrange
        widget = MultiSelectParameterWidget("Test")
        new_options = ["New 1", "New 2", "New 3", "New 4"]
        initial = ["New 1", "New 3"]
        
        # Act
        widget.update_options(new_options, initial)
        
        # Assert
        assert widget.options == new_options
        assert widget.list_widget.count() == len(new_options)
        assert sorted(widget.value) == sorted(initial)
        
        # Check that the correct items are selected
        for i in range(widget.list_widget.count()):
            item = widget.list_widget.item(i)
            if item.text() in initial:
                assert item.isSelected()
            else:
                assert not item.isSelected()

    def test_update_options_with_invalid_initial(self, qapp):
        """
        Test updating options with invalid initial values.
        
        Verifies:
        - Options are updated
        - List widget contains all options
        - Invalid initial values are ignored
        - Valid initial values are selected
        """
        # Arrange
        widget = MultiSelectParameterWidget("Test")
        new_options = ["New 1", "New 2", "New 3"]
        initial = ["New 1", "Invalid", "New 3"]
        
        # Act
        widget.update_options(new_options, initial)
        
        # Assert
        assert widget.options == new_options
        assert widget.list_widget.count() == len(new_options)
        assert sorted(widget.value) == ["New 1", "New 3"]

    def test_update_options_no_initial(self, qapp):
        """
        Test updating options without specifying initial values.
        
        Verifies:
        - Options are updated
        - List widget contains all options
        - No items are selected
        - Value is reset to empty list
        """
        # Arrange
        widget = MultiSelectParameterWidget("Test", {
            "initial": ["Old Value"]
        })
        new_options = ["New 1", "New 2", "New 3"]
        
        # Act
        widget.update_options(new_options)
        
        # Assert
        assert widget.options == new_options
        assert widget.list_widget.count() == len(new_options)
        assert widget.value == []
        
        # Check that no items are selected
        for i in range(widget.list_widget.count()):
            assert not widget.list_widget.item(i).isSelected()

    def test_integration_user_interaction(self, qtbot_extended):
        """
        Integration test for user interaction with the list widget.
        
        Verifies:
        - User can select and deselect items
        - Changing selection updates the value
        - valueChanged signal is emitted with correct parameters
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        widget = MultiSelectParameterWidget("Test", {"options": options})
        qtbot_extended.addWidget(widget)
        
        # Mock the callback function
        callback = MagicMock()
        widget.register_callback(callback)
        
        # Act - Simulate user clicking items
        qtbot_extended.mouseClick(widget.list_widget.viewport(), Qt.LeftButton, 
                                 pos=widget.list_widget.visualItemRect(widget.list_widget.item(0)).center())
        qtbot_extended.mouseClick(widget.list_widget.viewport(), Qt.LeftButton,
                                 pos=widget.list_widget.visualItemRect(widget.list_widget.item(2)).center())
        
        # Assert
        assert sorted(widget.value) == ["Option 1", "Option 3"]
        callback.assert_called_with("Test", ["Option 1", "Option 3"])

    def test_integration_signal_emission(self, qtbot_extended):
        """
        Integration test for signal emission.
        
        Verifies:
        - Signals are properly emitted when selection changes
        - Signals contain the correct parameters
        """
        # Arrange
        options = ["Option 1", "Option 2", "Option 3", "Option 4"]
        widget = MultiSelectParameterWidget("Test", {"options": options})
        qtbot_extended.addWidget(widget)
        
        # Use qtbot to spy on the signal
        with qtbot_extended.waitSignal(widget.valueChanged, timeout=1000) as blocker:
            # Act - Select an item
            widget.list_widget.item(1).setSelected(True)
            widget.on_selection_changed()
        
        # Assert
        assert blocker.args == ["Test", ["Option 2"]]
        assert widget.value == ["Option 2"]