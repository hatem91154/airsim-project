"""
Industrial-level test suite for the ParametersContainer class.

This module tests the functionality of the ParametersContainer class,
which manages parameter widgets and parameter groups.
"""
import pytest
from unittest.mock import MagicMock, patch

from PyQt5.QtWidgets import QWidget, QVBoxLayout

from pyqt_live_tuner.containers.parameters_container import ParametersContainer
from pyqt_live_tuner.parameter_widgets import (
    ParameterWidget, FloatParameterWidget, BoolParameterWidget, DropdownParameterWidget
)
from pyqt_live_tuner.parameter_groups import (
    ParameterGroupWidget, LinkedParameterGroup
)


class TestParametersContainer:
    """Comprehensive test suite for ParametersContainer class."""

    def test_initialization(self, qapp):
        """
        Test ParametersContainer initialization.
        
        Verifies:
        - Container is properly initialized
        - Layout is created
        - Widgets collection is empty
        - Groups collection is empty
        """
        # Act
        container = ParametersContainer()
        
        # Assert
        assert container.layout is not None
        assert isinstance(container.layout, QVBoxLayout)
        assert isinstance(container.widgets, dict)
        assert len(container.widgets) == 0
        assert isinstance(container.groups, list)
        assert len(container.groups) == 0
        assert container.isWidgetResizable()

    def test_add_param(self, qapp):
        """
        Test adding a parameter widget to the container.
        
        Verifies:
        - Parameter is added to the widgets collection
        - A frame is created for the parameter
        - The parameter is added to the layout
        """
        # Arrange
        container = ParametersContainer()
        param = FloatParameterWidget("Test Parameter")
        original_layout_count = container.layout.count()
        
        # Act
        container.add_param(param)
        
        # Assert
        assert "Test Parameter" in container.widgets
        assert container.widgets["Test Parameter"] is param
        assert container.layout.count() > original_layout_count

    def test_add_multiple_params(self, qapp):
        """
        Test adding multiple parameter widgets to the container.
        
        Verifies:
        - Multiple parameters are added correctly
        - Parameters maintain their identities in the widgets collection
        """
        # Arrange
        container = ParametersContainer()
        param1 = FloatParameterWidget("Float Param")
        param2 = BoolParameterWidget("Bool Param")
        param3 = DropdownParameterWidget("Dropdown Param")
        
        # Act
        container.add_param(param1)
        container.add_param(param2)
        container.add_param(param3)
        
        # Assert
        assert len(container.widgets) == 3
        assert "Float Param" in container.widgets
        assert "Bool Param" in container.widgets
        assert "Dropdown Param" in container.widgets
        assert container.widgets["Float Param"] is param1
        assert container.widgets["Bool Param"] is param2
        assert container.widgets["Dropdown Param"] is param3

    def test_add_param_overwrite(self, qapp):
        """
        Test adding a parameter with a name that already exists.
        
        Verifies:
        - New parameter overwrites the existing one in the widgets collection
        """
        # Arrange
        container = ParametersContainer()
        param1 = FloatParameterWidget("Same Name")
        param2 = BoolParameterWidget("Same Name")
        
        # Act
        container.add_param(param1)
        container.add_param(param2)
        
        # Assert
        assert len(container.widgets) == 1
        assert container.widgets["Same Name"] is param2

    def test_add_group(self, qapp):
        """
        Test adding a parameter group to the container.
        
        Verifies:
        - Group is added to the groups collection
        - Group is added to the layout
        """
        # Arrange
        container = ParametersContainer()
        group = LinkedParameterGroup("Test Group")
        original_layout_count = container.layout.count()
        
        # Act
        container.add_group(group)
        
        # Assert
        assert group in container.groups
        assert container.layout.count() > original_layout_count

    def test_add_multiple_groups(self, qapp):
        """
        Test adding multiple parameter groups to the container.
        
        Verifies:
        - Multiple groups are added correctly
        - Groups maintain their identities in the groups collection
        """
        # Arrange
        container = ParametersContainer()
        group1 = LinkedParameterGroup("Group 1")
        group2 = LinkedParameterGroup("Group 2")
        group3 = LinkedParameterGroup("Group 3")
        
        # Act
        container.add_group(group1)
        container.add_group(group2)
        container.add_group(group3)
        
        # Assert
        assert len(container.groups) == 3
        assert group1 in container.groups
        assert group2 in container.groups
        assert group3 in container.groups

    def test_get_values_empty(self, qapp):
        """
        Test getting values from an empty container.
        
        Verifies:
        - Result is an empty dictionary
        """
        # Arrange
        container = ParametersContainer()
        
        # Act
        values = container.get_values()
        
        # Assert
        assert isinstance(values, dict)
        assert len(values) == 0

    def test_get_values_with_params(self, qapp):
        """
        Test getting values from a container with parameters.
        
        Verifies:
        - Result contains all parameter values
        - Values are associated with correct parameter names
        """
        # Arrange
        container = ParametersContainer()
        param1 = FloatParameterWidget("Float Param")
        param2 = BoolParameterWidget("Bool Param")
        
        # Mock the get_value methods
        param1.get_value = MagicMock(return_value=5.0)
        param2.get_value = MagicMock(return_value=True)
        
        container.add_param(param1)
        container.add_param(param2)
        
        # Act
        values = container.get_values()
        
        # Assert
        assert len(values) == 2
        assert values["Float Param"] == 5.0
        assert values["Bool Param"] is True
        param1.get_value.assert_called_once()
        param2.get_value.assert_called_once()

    def test_get_values_with_groups(self, qapp):
        """
        Test getting values from a container with parameter groups.
        
        Verifies:
        - Result contains all group values
        - Group values are nested under the group titles
        """
        # Arrange
        container = ParametersContainer()
        group = LinkedParameterGroup("Test Group")
        
        # Mock the get_values method
        group.get_values = MagicMock(return_value={"Param1": 10, "Param2": 20})
        
        container.add_group(group)
        
        # Act
        values = container.get_values()
        
        # Assert
        assert len(values) == 1
        assert "Test Group" in values
        assert values["Test Group"] == {"Param1": 10, "Param2": 20}
        group.get_values.assert_called_once()

    def test_get_values_with_params_and_groups(self, qapp):
        """
        Test getting values from a container with both parameters and groups.
        
        Verifies:
        - Result contains both parameter values and group values
        - Parameters are at the top level and groups are nested
        """
        # Arrange
        container = ParametersContainer()
        param = FloatParameterWidget("Float Param")
        group = LinkedParameterGroup("Test Group")
        
        # Mock the get_value and get_values methods
        param.get_value = MagicMock(return_value=5.0)
        group.get_values = MagicMock(return_value={"Param1": 10, "Param2": 20})
        group.title = MagicMock(return_value="Test Group")
        
        container.add_param(param)
        container.add_group(group)
        
        # Act
        values = container.get_values()
        
        # Assert
        assert len(values) == 2
        assert values["Float Param"] == 5.0
        assert values["Test Group"] == {"Param1": 10, "Param2": 20}
        param.get_value.assert_called_once()
        group.get_values.assert_called_once()
        group.title.assert_called()

    def test_set_values_empty(self, qapp):
        """
        Test setting values on an empty container.
        
        Verifies:
        - No error occurs when setting values on an empty container
        """
        # Arrange
        container = ParametersContainer()
        
        # Act & Assert (no exception should be raised)
        container.set_values({})
        container.set_values({"Param": 10})  # No matching parameter

    def test_set_values_with_params(self, qapp):
        """
        Test setting values on a container with parameters.
        
        Verifies:
        - Parameter values are set correctly
        - Only parameters with matching names are set
        """
        # Arrange
        container = ParametersContainer()
        param1 = FloatParameterWidget("Float Param")
        param2 = BoolParameterWidget("Bool Param")
        
        # Mock the set_value methods
        param1.set_value = MagicMock()
        param2.set_value = MagicMock()
        
        container.add_param(param1)
        container.add_param(param2)
        
        # Act
        container.set_values({
            "Float Param": 7.5,
            "Bool Param": False,
            "Non-existent Param": "Ignored"
        })
        
        # Assert
        param1.set_value.assert_called_once_with(7.5)
        param2.set_value.assert_called_once_with(False)

    def test_set_values_with_groups(self, qapp):
        """
        Test setting values on a container with parameter groups.
        
        Verifies:
        - Group values are set correctly
        - Only groups with matching titles are set
        """
        # Arrange
        container = ParametersContainer()
        group1 = LinkedParameterGroup("Group 1")
        group2 = LinkedParameterGroup("Group 2")
        
        # Mock the set_values methods and title methods
        group1.set_values = MagicMock()
        group2.set_values = MagicMock()
        group1.title = MagicMock(return_value="Group 1")
        group2.title = MagicMock(return_value="Group 2")
        
        container.add_group(group1)
        container.add_group(group2)
        
        # Act
        container.set_values({
            "Group 1": {"Param1": 10, "Param2": 20},
            "Group 2": {"Param3": 30, "Param4": 40},
            "Non-existent Group": {"Param5": 50}
        })
        
        # Assert
        group1.set_values.assert_called_once_with({"Param1": 10, "Param2": 20})
        group2.set_values.assert_called_once_with({"Param3": 30, "Param4": 40})
        group1.title.assert_called()
        group2.title.assert_called()

    def test_set_values_with_params_and_groups(self, qapp):
        """
        Test setting values on a container with both parameters and groups.
        
        Verifies:
        - Parameter values and group values are set correctly
        - Only parameters and groups with matching names/titles are set
        """
        # Arrange
        container = ParametersContainer()
        param = FloatParameterWidget("Float Param")
        group = LinkedParameterGroup("Test Group")
        
        # Mock the set_value and set_values methods
        param.set_value = MagicMock()
        group.set_values = MagicMock()
        group.title = MagicMock(return_value="Test Group")
        
        container.add_param(param)
        container.add_group(group)
        
        # Act
        container.set_values({
            "Float Param": 7.5,
            "Test Group": {"Param1": 10, "Param2": 20},
            "Non-existent": "Ignored"
        })
        
        # Assert
        param.set_value.assert_called_once_with(7.5)
        group.set_values.assert_called_once_with({"Param1": 10, "Param2": 20})
        group.title.assert_called()

    def test_integration_with_real_widgets(self, qtbot_extended):
        """
        Integration test with real widgets instead of mocks.
        
        Verifies:
        - Container works correctly with real widget instances
        - Values can be set and retrieved from real widgets
        """
        # Arrange
        container = ParametersContainer()
        qtbot_extended.addWidget(container)
        
        float_param = FloatParameterWidget("Float", {"initial": 5.0, "min": 0, "max": 10})
        bool_param = BoolParameterWidget("Boolean", {"initial": True})
        dropdown_param = DropdownParameterWidget("Dropdown", {
            "options": ["Option 1", "Option 2", "Option 3"],
            "initial": "Option 2"
        })
        
        # Add parameters
        container.add_param(float_param)
        container.add_param(bool_param)
        container.add_param(dropdown_param)
        
        # Create and add a group
        group = LinkedParameterGroup("Group")
        group.add_parameter(FloatParameterWidget("GroupParam1", {"initial": 1.0}))
        group.add_parameter(BoolParameterWidget("GroupParam2", {"initial": False}))
        container.add_group(group)
        
        # Act - Get initial values
        initial_values = container.get_values()
        
        # Change some values
        float_param.set_value(7.5)
        bool_param.set_value(False)
        
        # Set group values
        group_values = {"GroupParam1": 2.0, "GroupParam2": True}
        group.set_values(group_values)
        
        # Act - Get updated values
        updated_values = container.get_values()
        
        # Assert initial values
        assert initial_values["Float"] == 5.0
        assert initial_values["Boolean"] is True
        assert initial_values["Dropdown"] == "Option 2"
        assert "Group" in initial_values
        assert initial_values["Group"]["GroupParam1"] == 1.0
        assert initial_values["Group"]["GroupParam2"] is False
        
        # Assert updated values
        assert updated_values["Float"] == 7.5
        assert updated_values["Boolean"] is False
        assert updated_values["Dropdown"] == "Option 2"  # Unchanged
        assert updated_values["Group"]["GroupParam1"] == 2.0
        assert updated_values["Group"]["GroupParam2"] is True

    def test_integration_save_load_values(self, qtbot_extended, temp_json_file):
        """
        Integration test for saving and loading values.
        
        Verifies:
        - Values can be saved to JSON and loaded back
        - Container properly restores values from loaded JSON
        """
        import json
        
        # Arrange
        container = ParametersContainer()
        qtbot_extended.addWidget(container)
        
        # Add parameters and a group
        container.add_param(FloatParameterWidget("Float", {"initial": 5.0}))
        container.add_param(BoolParameterWidget("Boolean", {"initial": True}))
        
        group = LinkedParameterGroup("Group")
        group.add_parameter(FloatParameterWidget("GroupParam", {"initial": 1.0}))
        container.add_group(group)
        
        # Act - Save values to JSON file
        values = container.get_values()
        with open(temp_json_file, 'w') as f:
            json.dump(values, f)
        
        # Change values
        container.set_values({
            "Float": 7.5,
            "Boolean": False,
            "Group": {"GroupParam": 2.0}
        })
        
        # Act - Load values back
        with open(temp_json_file, 'r') as f:
            loaded_values = json.load(f)
        container.set_values(loaded_values)
        
        # Get final values
        final_values = container.get_values()
        
        # Assert
        assert final_values["Float"] == 5.0
        assert final_values["Boolean"] is True
        assert final_values["Group"]["GroupParam"] == 1.0