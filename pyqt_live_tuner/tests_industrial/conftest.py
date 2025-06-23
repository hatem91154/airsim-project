"""
Industrial-level test suite configuration for PyQt Live Tuner.

This file contains pytest fixtures and configuration that are shared across
all test modules in the industrial testing suite.
"""
import os
import sys
import pytest
import json
import tempfile
from unittest.mock import MagicMock, patch
from pathlib import Path

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QSize

# Add project root to sys.path to ensure imports work correctly
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Create a QApplication instance for tests that need it
@pytest.fixture(scope="session")
def qapp():
    """
    Create a QApplication instance for the test session.
    
    This fixture ensures we have a single QApplication instance throughout the test session,
    which is a requirement for Qt applications.
    """
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    # No cleanup needed since the app will be terminated after the session

@pytest.fixture
def qtbot_extended(qtbot):
    """
    Enhanced qtbot fixture with additional utility methods.
    """
    # Add custom helper methods to the qtbot
    def get_widget_text(widget):
        """Get text from various widget types."""
        if hasattr(widget, 'text'):
            return widget.text()
        elif hasattr(widget, 'toPlainText'):
            return widget.toPlainText()
        elif hasattr(widget, 'displayText'):
            return widget.displayText()
        elif hasattr(widget, 'currentText'):
            return widget.currentText()
        else:
            raise ValueError(f"Cannot extract text from widget type: {type(widget)}")
    
    def verify_signal_emitted(signal, timeout=1000):
        """Verify that a signal is emitted within the timeout period."""
        spy = qtbot.waitSignal(signal, timeout=timeout)
        assert spy.signal_triggered, f"Signal {signal} was not emitted within {timeout}ms"
        return spy.args
    
    # Attach the methods to qtbot
    qtbot.get_widget_text = get_widget_text
    qtbot.verify_signal_emitted = verify_signal_emitted
    
    return qtbot

@pytest.fixture
def temp_json_file():
    """
    Create a temporary JSON file for testing configuration save/load operations.
    """
    with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp:
        yield temp.name
    # Clean up after test
    if os.path.exists(temp.name):
        os.unlink(temp.name)

@pytest.fixture
def sample_config_data():
    """
    Provide sample configuration data for testing.
    """
    return {
        "Float Parameter": 5.0,
        "Boolean Parameter": True,
        "Dropdown Parameter": "Option 2",
        "String Parameter": "Hello World",
        "PID Controller": {
            "Kp": 0.5,
            "Ki": 0.1,
            "Kd": 0.25
        },
        "Image Processing": {
            "Brightness": 0,
            "Contrast": 100,
            "Apply Sharpening": False,
            "Filter Type": "None"
        }
    }

@pytest.fixture
def mock_qfiledialog():
    """
    Mock QFileDialog for testing file operations without actual dialogs.
    """
    with patch('PyQt5.QtWidgets.QFileDialog') as mock:
        yield mock

@pytest.fixture
def mock_qmessagebox():
    """
    Mock QMessageBox for testing message dialogs without actual popups.
    """
    with patch('PyQt5.QtWidgets.QMessageBox') as mock:
        yield mock