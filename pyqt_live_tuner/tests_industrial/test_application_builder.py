"""
Industrial-level test suite for the ApplicationBuilder class.

This module tests the core functionality of the ApplicationBuilder class,
ensuring proper initialization, window creation, and application execution.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import sys
from pathlib import Path

# Import the modules being tested
from pyqt_live_tuner.application_builder import ApplicationBuilder, _Application
from pyqt_live_tuner.main_application import MainApplication


class TestApplicationBuilder:
    """Comprehensive test suite for ApplicationBuilder class."""

    def test_initialization_default_params(self, qapp):
        """
        Test ApplicationBuilder initialization with default parameters.
        
        Verifies:
        - The builder creates a MainApplication instance
        - The default title is applied correctly
        - The QApplication is correctly referenced
        """
        # Arrange & Act
        builder = ApplicationBuilder()
        
        # Assert
        assert builder.main_window is not None
        assert isinstance(builder.main_window, MainApplication)
        assert builder.main_window.windowTitle() == "My Application"
        assert builder._app is _Application

    def test_initialization_custom_title(self, qapp):
        """
        Test ApplicationBuilder initialization with a custom title.
        
        Verifies:
        - The custom title is applied correctly to the MainApplication
        """
        # Arrange & Act
        custom_title = "Custom Test Application"
        builder = ApplicationBuilder(title=custom_title)
        
        # Assert
        assert builder.main_window.windowTitle() == custom_title

    @patch('pyqt_live_tuner.application_builder._Application.exec')
    def test_run_method(self, mock_exec, qapp):
        """
        Test the run method functionality.
        
        Verifies:
        - The main window's show method is called
        - QApplication.exec() is called to start the event loop
        """
        # Arrange
        builder = ApplicationBuilder()
        builder.main_window.show = MagicMock()
        
        # Act
        builder.run()
        
        # Assert
        builder.main_window.show.assert_called_once()
        mock_exec.assert_called_once()

    def test_multiple_instances_share_qapplication(self, qapp):
        """
        Test that multiple ApplicationBuilder instances share the same QApplication.
        
        Verifies:
        - QApplication is correctly implemented as a singleton
        - All ApplicationBuilder instances reference the same QApplication
        """
        # Arrange & Act
        builder1 = ApplicationBuilder()
        builder2 = ApplicationBuilder()
        
        # Assert
        assert builder1._app is _Application
        assert builder2._app is _Application
        assert builder1._app is builder2._app

    @patch('qdarktheme.setup_theme')
    def test_dark_theme_setup(self, mock_setup_theme):
        """
        Test that dark theme is set up during module import.
        
        Verifies:
        - The setup_theme function is called with the correct theme
        """
        # Force module reload to trigger theme setup again
        import importlib
        import pyqt_live_tuner.application_builder
        importlib.reload(pyqt_live_tuner.application_builder)
        
        # Assert
        mock_setup_theme.assert_called_with("dark")

    def test_integration_create_and_show(self, qtbot):
        """
        Integration test for creating and showing the application.
        
        Verifies:
        - The application window can be created and shown without errors
        - The window has the correct properties after showing
        """
        # Arrange
        builder = ApplicationBuilder(title="Integration Test")
        
        # Add the window to qtbot to properly manage it
        qtbot.addWidget(builder.main_window)
        
        # Act - Show the window (but don't run the event loop)
        builder.main_window.show()
        
        # Assert
        assert builder.main_window.isVisible()
        assert builder.main_window.windowTitle() == "Integration Test"
        assert builder.main_window.width() >= builder.main_window.minimumWidth()
        
        # Cleanup
        builder.main_window.close()

    def test_exception_handling(self, monkeypatch):
        """
        Test exception handling during initialization.
        
        Verifies:
        - Exceptions during MainApplication initialization are properly propagated
        """
        # Arrange
        def mock_init(*args, **kwargs):
            raise RuntimeError("Simulated initialization error")
        
        monkeypatch.setattr(MainApplication, '__init__', mock_init)
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Simulated initialization error"):
            ApplicationBuilder()