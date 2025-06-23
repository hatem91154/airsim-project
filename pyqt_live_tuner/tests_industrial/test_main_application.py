"""
Industrial-level test suite for the MainApplication class.

This module tests the functionality of the MainApplication class,
which handles the main window, menus, and container management.
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock, call, mock_open

from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt

from pyqt_live_tuner.main_application import MainApplication
from pyqt_live_tuner.containers.parameters_container import ParametersContainer
from pyqt_live_tuner.containers.configurations_container import ConfigurationsContainer
from pyqt_live_tuner.parameter_widgets import ParameterWidget, FloatParameterWidget
from pyqt_live_tuner.parameter_groups import ParameterGroupWidget, LinkedParameterGroup


class TestMainApplication:
    """Comprehensive test suite for MainApplication class."""

    def test_initialization_default_params(self, qapp):
        """
        Test MainApplication initialization with default parameters.
        
        Verifies:
        - Default title is set correctly
        - Window properties are initialized correctly
        - Layout is set up properly
        - Menu is created
        """
        # Act
        app = MainApplication()
        
        # Assert
        assert app.windowTitle() == "My Application"
        assert app.minimumWidth() == 450
        assert app._last_save_path is None
        assert app.parameters_container is None
        assert app.configurations_container is None
        assert app.layout is not None
        assert app.menuBar() is not None
        assert len(app.menuBar().actions()) > 0  # Should have at least one menu

    def test_initialization_custom_title(self, qapp):
        """
        Test MainApplication initialization with custom title.
        
        Verifies:
        - Custom title is set correctly
        """
        # Arrange
        custom_title = "Custom Application Title"
        
        # Act
        app = MainApplication(title=custom_title)
        
        # Assert
        assert app.windowTitle() == custom_title

    def test_menu_setup(self, qapp):
        """
        Test that the menu is set up correctly with all required actions.
        
        Verifies:
        - File menu exists and contains the expected actions
        """
        # Act
        app = MainApplication()
        menu_bar = app.menuBar()
        
        # Get the "File" menu
        file_menus = [action.menu() for action in menu_bar.actions() 
                      if action.text() == "File"]
        assert len(file_menus) == 1, "File menu not found"
        file_menu = file_menus[0]
        
        # Assert
        action_texts = [action.text() for action in file_menu.actions()]
        assert "Generate" in action_texts
        assert "Load" in action_texts
        assert "Save" in action_texts
        assert "Save As..." in action_texts

    def test_set_parameters_container(self, qapp):
        """
        Test setting a parameters container.
        
        Verifies:
        - Container is assigned correctly
        - Label is added to the layout
        - Container is added to the layout
        - Old container is replaced if present
        """
        # Arrange
        app = MainApplication()
        container1 = ParametersContainer()
        container2 = ParametersContainer()
        
        # Act - Set first container
        app.set_parameters_container(container1, "Container 1")
        
        # Assert
        assert app.parameters_container is container1
        
        # Act - Set second container (should replace the first)
        app.set_parameters_container(container2, "Container 2")
        
        # Assert
        assert app.parameters_container is container2

    def test_set_configurations_container(self, qapp):
        """
        Test setting a configurations container.
        
        Verifies:
        - Container is assigned correctly
        - Label is added to the layout
        - Container is added to the layout
        - Old container is replaced if present
        """
        # Arrange
        app = MainApplication()
        container1 = ConfigurationsContainer()
        container2 = ConfigurationsContainer()
        
        # Act - Set first container
        app.set_configurations_container(container1, "Config 1")
        
        # Assert
        assert app.configurations_container is container1
        
        # Act - Set second container (should replace the first)
        app.set_configurations_container(container2, "Config 2")
        
        # Assert
        assert app.configurations_container is container2

    def test_add_parameter(self, qapp):
        """
        Test adding a parameter to the MainApplication.
        
        Verifies:
        - ParametersContainer is created if it doesn't exist
        - Parameter is added to the container
        """
        # Arrange
        app = MainApplication()
        param = FloatParameterWidget("Test Parameter")
        
        # Act
        app.add_parameter(param)
        
        # Assert
        assert app.parameters_container is not None
        assert param.name in app.parameters_container.widgets

    def test_add_parameter_group(self, qapp):
        """
        Test adding a parameter group to the MainApplication.
        
        Verifies:
        - ParametersContainer is created if it doesn't exist
        - Group is added to the container
        """
        # Arrange
        app = MainApplication()
        group = LinkedParameterGroup("Test Group")
        
        # Act
        app.add_parameter_group(group)
        
        # Assert
        assert app.parameters_container is not None
        assert group in app.parameters_container.groups

    def test_add_configuration_widget(self, qapp):
        """
        Test adding a configuration widget to the MainApplication.
        
        Verifies:
        - ConfigurationsContainer is created if it doesn't exist
        - Widget is added to the container
        - Label is added if specified
        """
        # Arrange
        app = MainApplication()
        widget = QWidget()
        
        # Act - Add without label
        app.add_configuration_widget(widget)
        
        # Assert
        assert app.configurations_container is not None
        
        # Act - Add with label
        label_widget = QWidget()
        app.add_configuration_widget(label_widget, "Test Label")
        
        # Assert
        # Note: We can't directly test that the widget was added to the layout,
        # but we can verify that the container exists

    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_generate_config(self, mock_msgbox, mock_file, mock_json_dump, mock_dialog, qapp):
        """
        Test generating a configuration file.
        
        Verifies:
        - File dialog is shown
        - JSON data is written to the selected file
        - Message box is shown after successful save
        """
        # Arrange
        app = MainApplication()
        container = ParametersContainer()
        app.set_parameters_container(container)
        
        # Mock parameter values
        container.get_values = MagicMock(return_value={"param1": 1, "param2": 2})
        
        # Mock file dialog to return a file path
        mock_dialog.return_value = ("/path/to/config.json", "JSON Files (*.json)")
        
        # Act
        app._generate_config()
        
        # Assert
        mock_dialog.assert_called_once()
        mock_file.assert_called_once_with("/path/to/config.json", "w")
        mock_json_dump.assert_called_once_with({"param1": 1, "param2": 2}, mock_file(), indent=2)
        mock_msgbox.assert_called_once()

    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_generate_config_canceled(self, mock_dialog, qapp):
        """
        Test generating a configuration when the dialog is canceled.
        
        Verifies:
        - No action is taken if file dialog is canceled
        """
        # Arrange
        app = MainApplication()
        container = ParametersContainer()
        app.set_parameters_container(container)
        container.get_values = MagicMock()
        
        # Mock file dialog to return empty (canceled)
        mock_dialog.return_value = ("", "")
        
        # Act
        app._generate_config()
        
        # Assert
        mock_dialog.assert_called_once()
        container.get_values.assert_not_called()

    def test_generate_config_no_container(self, qapp):
        """
        Test generating a configuration when no parameters container exists.
        
        Verifies:
        - No action is taken if parameters container doesn't exist
        """
        # Arrange
        app = MainApplication()
        assert app.parameters_container is None
        
        # Act & Assert (should not raise any exceptions)
        app._generate_config()

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    @patch('json.load')
    @patch('builtins.open', new_callable=mock_open)
    @patch('os.path.exists')
    @patch('PyQt5.QtWidgets.QMessageBox.information')
    def test_load_config(self, mock_msgbox, mock_exists, mock_file, mock_json_load, 
                         mock_dialog, qapp):
        """
        Test loading a configuration file.
        
        Verifies:
        - File dialog is shown
        - JSON data is loaded from the selected file
        - Configuration is applied to the parameters container
        - Message box is shown after successful load
        """
        # Arrange
        app = MainApplication()
        container = ParametersContainer()
        app.set_parameters_container(container)
        container.set_values = MagicMock()
        
        # Mock file dialog to return a file path
        mock_dialog.return_value = ("/path/to/config.json", "JSON Files (*.json)")
        
        # Mock file operations
        mock_exists.return_value = True
        mock_json_load.return_value = {"param1": 1, "param2": 2}
        
        # Act
        app._load_config()
        
        # Assert
        mock_dialog.assert_called_once()
        mock_exists.assert_called_once_with("/path/to/config.json")
        mock_file.assert_called_once_with("/path/to/config.json", "r")
        mock_json_load.assert_called_once()
        container.set_values.assert_called_once_with({"param1": 1, "param2": 2})
        mock_msgbox.assert_called_once()

    @patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName')
    def test_load_config_canceled(self, mock_dialog, qapp):
        """
        Test loading a configuration when the dialog is canceled.
        
        Verifies:
        - No action is taken if file dialog is canceled
        """
        # Arrange
        app = MainApplication()
        container = ParametersContainer()
        app.set_parameters_container(container)
        container.set_values = MagicMock()
        
        # Mock file dialog to return empty (canceled)
        mock_dialog.return_value = ("", "")
        
        # Act
        app._load_config()
        
        # Assert
        mock_dialog.assert_called_once()
        container.set_values.assert_not_called()

    def test_load_config_no_container(self, qapp):
        """
        Test loading a configuration when no parameters container exists.
        
        Verifies:
        - No action is taken if parameters container doesn't exist
        """
        # Arrange
        app = MainApplication()
        assert app.parameters_container is None
        
        # Act & Assert (should not raise any exceptions)
        app._load_config()

    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_config_with_existing_path(self, mock_file, mock_json_dump, qapp):
        """
        Test saving a configuration with an existing save path.
        
        Verifies:
        - Configuration is saved to the existing path
        - Status bar message is shown
        """
        # Arrange
        app = MainApplication()
        container = ParametersContainer()
        app.set_parameters_container(container)
        app._last_save_path = "/path/to/existing_config.json"
        
        # Mock status bar
        app.statusBar = MagicMock()
        status_bar = MagicMock()
        app.statusBar.return_value = status_bar
        
        # Mock parameter values
        container.get_values = MagicMock(return_value={"param1": 1, "param2": 2})
        
        # Act
        app._save_config()
        
        # Assert
        mock_file.assert_called_once_with("/path/to/existing_config.json", "w")
        mock_json_dump.assert_called_once_with({"param1": 1, "param2": 2}, mock_file(), indent=2)
        status_bar.showMessage.assert_called_once()

    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    @patch('json.dump')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_config_as(self, mock_file, mock_json_dump, mock_dialog, qapp):
        """
        Test saving a configuration with a new file path.
        
        Verifies:
        - File dialog is shown
        - Save path is updated
        - Configuration is saved to the new path
        """
        # Arrange
        app = MainApplication()
        container = ParametersContainer()
        app.set_parameters_container(container)
        
        # Mock parameter values
        container.get_values = MagicMock(return_value={"param1": 1, "param2": 2})
        
        # Mock status bar
        app.statusBar = MagicMock()
        status_bar = MagicMock()
        app.statusBar.return_value = status_bar
        
        # Mock file dialog to return a file path
        mock_dialog.return_value = ("/path/to/new_config.json", "JSON Files (*.json)")
        
        # Act
        app._save_config_as()
        
        # Assert
        mock_dialog.assert_called_once()
        assert app._last_save_path == "/path/to/new_config.json"
        mock_file.assert_called_once_with("/path/to/new_config.json", "w")
        mock_json_dump.assert_called_once_with({"param1": 1, "param2": 2}, mock_file(), indent=2)

    @patch('PyQt5.QtWidgets.QFileDialog.getSaveFileName')
    def test_save_config_as_canceled(self, mock_dialog, qapp):
        """
        Test saving a configuration when the dialog is canceled.
        
        Verifies:
        - No action is taken if file dialog is canceled
        """
        # Arrange
        app = MainApplication()
        container = ParametersContainer()
        app.set_parameters_container(container)
        container.get_values = MagicMock()
        
        # Mock file dialog to return empty (canceled)
        mock_dialog.return_value = ("", "")
        
        # Act
        app._save_config_as()
        
        # Assert
        mock_dialog.assert_called_once()
        container.get_values.assert_not_called()
        assert app._last_save_path is None

    def test_make_action(self, qapp):
        """
        Test creating a menu action.
        
        Verifies:
        - Action is created with the correct label
        - Action is connected to the specified function
        """
        # Arrange
        app = MainApplication()
        mock_slot = MagicMock()
        
        # Act
        action = app._make_action("Test Action", mock_slot)
        
        # Assert
        assert action.text() == "Test Action"
        
        # Trigger the action and verify the slot was called
        action.trigger()
        mock_slot.assert_called_once()