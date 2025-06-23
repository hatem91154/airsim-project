"""
Industrial-level test suite for the FloatParameterWidget class.

This module focuses on testing the FloatParameterWidget class with
particular attention to step size change behaviors and value preservation.
"""
import pytest
from unittest.mock import MagicMock, patch
import time

from PyQt5.QtWidgets import QDoubleSpinBox, QSlider
from PyQt5.QtCore import Qt
from PyQt5.QtTest import QTest

from pyqt_live_tuner.parameter_widgets.float_parameter_widget import FloatParameterWidget
from pyqt_live_tuner.parameter_widgets.adjust_dialog import AdjustDialog


class TestFloatParameterWidget:
    """Comprehensive test suite for FloatParameterWidget class with focus on step size changes."""

    def test_initialization_default_params(self, qapp):
        """
        Test initialization with default parameters.
        
        Verifies:
        - Widget is properly initialized with default parameters
        - All UI controls are created and configured correctly
        """
        # Act
        widget = FloatParameterWidget()
        
        # Assert
        assert widget.name == "Unnamed"
        assert widget.min_val == 0.0
        assert widget.max_val == 1.0
        assert widget.step == 0.01
        assert widget.value == 0.0
        assert widget._updating_controls is False
        
        # Check UI controls
        assert widget.spinbox is not None
        assert isinstance(widget.spinbox, QDoubleSpinBox)
        assert widget.slider is not None
        assert isinstance(widget.slider, QSlider)
        assert widget.spinbox.minimum() == widget.min_val
        assert widget.spinbox.maximum() == widget.max_val
        assert widget.spinbox.singleStep() == widget.step
        assert widget.spinbox.value() == widget.value

    def test_initialization_with_config(self, qapp):
        """
        Test initialization with custom configuration.
        
        Verifies:
        - Configuration parameters are applied correctly
        - UI controls reflect the configuration
        """
        # Arrange
        config = {
            "min": -10.0,
            "max": 10.0,
            "step": 0.5,
            "initial": 2.5,
            "decimal_places": 2
        }
        
        # Act
        widget = FloatParameterWidget("Custom", config)
        
        # Assert
        assert widget.name == "Custom"
        assert widget.min_val == -10.0
        assert widget.max_val == 10.0
        assert widget.step == 0.5
        assert widget.value == 2.5
        assert widget._decimal_places == 2
        
        # Check UI controls
        assert widget.spinbox.minimum() == widget.min_val
        assert widget.spinbox.maximum() == widget.max_val
        assert widget.spinbox.singleStep() == widget.step
        assert widget.spinbox.value() == widget.value
        assert widget.spinbox.decimals() == widget._decimal_places

    def test_on_spinbox_changed(self, qapp):
        """
        Test spinbox value change handling.
        
        Verifies:
        - Value is updated correctly when spinbox changes
        - Slider position is synced with the new value
        - valueChanged signal is emitted with correct parameters
        """
        # Arrange
        widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "step": 0.5})
        widget.valueChanged = MagicMock()
        widget._sync_slider = MagicMock()
        
        # Act
        widget.on_spinbox_changed(5.5)
        
        # Assert
        assert widget.value == 5.5
        widget._sync_slider.assert_called_once()
        widget.valueChanged.emit.assert_called_once_with("Test", 5.5)

    def test_on_slider_changed(self, qapp):
        """
        Test slider value change handling.
        
        Verifies:
        - Value is updated correctly when slider changes
        - Spinbox is updated with the new value
        - valueChanged signal is not emitted (happens on slider release)
        """
        # Arrange
        widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "step": 0.5})
        widget.valueChanged = MagicMock()
        widget.block_all_signals = MagicMock(wraps=widget.block_all_signals)
        
        # Act - simulate slider position at 50% (position 10 of 20 steps)
        widget.on_slider_changed(10)
        
        # Assert
        assert widget.value == 5.0  # 0 + 10 steps of 0.5
        widget.block_all_signals.assert_any_call(True)
        widget.block_all_signals.assert_any_call(False)
        widget.valueChanged.emit.assert_not_called()

    def test_set_value(self, qapp):
        """
        Test setting value programmatically.
        
        Verifies:
        - Value is updated correctly
        - Value is clamped to min/max range
        - Value is aligned to steps
        - UI controls are updated correctly
        """
        # Arrange
        widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "step": 0.5})
        widget._sync_slider = MagicMock()
        widget.block_all_signals = MagicMock(wraps=widget.block_all_signals)
        
        # Act - Set a value that aligns with steps
        widget.set_value(5.0)
        
        # Assert
        assert widget.value == 5.0
        assert widget.spinbox.value() == 5.0
        widget._sync_slider.assert_called_once()
        widget.block_all_signals.assert_any_call(True)
        widget.block_all_signals.assert_any_call(False)
        
        # Reset mocks
        widget._sync_slider.reset_mock()
        widget.block_all_signals.reset_mock()
        
        # Act - Set a value that needs to be aligned with steps
        widget.set_value(6.25)  # Should align to 6.0 or 6.5
        
        # Assert - Should round to nearest step (6.5)
        assert widget.value == 6.5
        assert widget.spinbox.value() == 6.5
        widget._sync_slider.assert_called_once()
        
        # Reset mocks
        widget._sync_slider.reset_mock()
        widget.block_all_signals.reset_mock()
        
        # Act - Set a value outside the range
        widget.set_value(12.0)  # Should clamp to max (10.0)
        
        # Assert
        assert widget.value == 10.0
        assert widget.spinbox.value() == 10.0
        widget._sync_slider.assert_called_once()

    def test_update_slider_range(self, qapp):
        """
        Test updating the slider range.
        
        Verifies:
        - Slider's maximum value is calculated correctly based on min, max, and step
        """
        # Arrange & Act
        widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "step": 0.5})
        
        # Assert
        # Should have (10-0)/0.5 = 20 steps
        assert widget.slider.maximum() == 20
        
        # Arrange & Act - Test with different parameters
        widget = FloatParameterWidget("Test", {"min": -5, "max": 5, "step": 0.1})
        
        # Assert
        # Should have (5-(-5))/0.1 = 100 steps
        assert widget.slider.maximum() == 100

    def test_configure_spinbox(self, qapp):
        """
        Test configuring the spinbox.
        
        Verifies:
        - Spinbox is configured with the correct parameters
        - Signal connections are properly managed
        """
        # Arrange
        widget = FloatParameterWidget()
        
        # Mock disconnect to prevent errors since we're testing internal method
        with patch.object(widget.spinbox, 'valueChanged'):
            # Set new parameters
            widget.min_val = -10.0
            widget.max_val = 10.0
            widget.step = 0.25
            widget.value = 5.0
            widget._decimal_places = 1
            
            # Act
            widget._configure_spinbox()
            
            # Assert
            assert widget.spinbox.minimum() == -10.0
            assert widget.spinbox.maximum() == 10.0
            assert widget.spinbox.singleStep() == 0.25
            assert widget.spinbox.value() == 5.0
            assert widget.spinbox.decimals() == 1

    def test_configure_slider(self, qapp):
        """
        Test configuring the slider.
        
        Verifies:
        - Slider is configured with the correct range
        - Slider position is set correctly based on value
        - Signal connections are properly managed
        """
        # Arrange
        widget = FloatParameterWidget()
        
        # Mock disconnect to prevent errors since we're testing internal method
        with patch.object(widget.slider, 'valueChanged'), \
             patch.object(widget.slider, 'sliderReleased'):
            
            # Set new parameters
            widget.min_val = 0.0
            widget.max_val = 10.0
            widget.step = 0.5
            widget.value = 5.0
            
            # Act
            widget._configure_slider()
            
            # Assert
            assert widget.slider.minimum() == 0
            assert widget.slider.maximum() == 20  # (10-0)/0.5 = 20 steps
            assert widget.slider.value() == 10    # At position 10 (halfway)

    def test_open_adjust_dialog_apply_changes(self, monkeypatch, qapp):
        """
        Test adjusting parameters through the dialog.
        
        Verifies:
        - Dialog is shown with current parameters
        - New parameters are applied correctly when dialog is accepted
        - Value is preserved but aligned to new step size
        - UI controls are reconfigured with new parameters
        """
        # Arrange
        widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "step": 1.0, "initial": 5.0})
        
        # Mock the AdjustDialog
        mock_dialog = MagicMock()
        mock_dialog.exec_.return_value = True  # Dialog accepted
        mock_dialog.get_values.return_value = (0.0, 10.0, 0.5)  # New min, max, step
        
        # Patch the AdjustDialog constructor
        monkeypatch.setattr('pyqt_live_tuner.parameter_widgets.adjust_dialog.AdjustDialog', 
                            lambda *args, **kwargs: mock_dialog)
        
        # Mock internal methods
        widget.block_all_signals = MagicMock(wraps=widget.block_all_signals)
        original_configure_spinbox = widget._configure_spinbox
        original_configure_slider = widget._configure_slider
        widget._configure_spinbox = MagicMock(wraps=original_configure_spinbox)
        widget._configure_slider = MagicMock(wraps=original_configure_slider)
        
        # Act
        widget.open_adjust_dialog()
        
        # Assert
        mock_dialog.exec_.assert_called_once()
        mock_dialog.get_values.assert_called_once()
        
        # Parameters should be updated
        assert widget.min_val == 0.0
        assert widget.max_val == 10.0
        assert widget.step == 0.5
        
        # Value should be preserved but aligned to new step
        assert widget.value == 5.0  # Original value was already aligned with new step
        
        # Methods should be called in the right order
        widget.block_all_signals.assert_any_call(True)
        widget._configure_spinbox.assert_called_once()
        widget._configure_slider.assert_called_once()
        widget.block_all_signals.assert_any_call(False)

    def test_step_change_value_preservation(self, monkeypatch, qapp):
        """
        Test that changing step size preserves the value as closely as possible.
        
        Verifies:
        - Value is preserved but aligned to new step size
        - When step size increases, value aligns to nearest valid step
        - When step size decreases, value aligns to nearest valid step
        """
        # Arrange - Create widget with initial parameters
        widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "step": 1.0, "initial": 3.0})
        
        # Configure mock dialog to change step to 0.5 (smaller step)
        mock_dialog = MagicMock()
        mock_dialog.exec_.return_value = True
        mock_dialog.get_values.return_value = (0.0, 10.0, 0.5)
        monkeypatch.setattr('pyqt_live_tuner.parameter_widgets.adjust_dialog.AdjustDialog', 
                            lambda *args, **kwargs: mock_dialog)
        
        # Act - Change step from 1.0 to 0.5
        widget.open_adjust_dialog()
        
        # Assert - Value should remain 3.0 since it aligns with 0.5 step
        assert widget.step == 0.5
        assert widget.value == 3.0
        
        # Update value to something not aligned with larger steps
        widget.set_value(3.25)
        assert widget.value == 3.5  # Should align to nearest 0.5 step
        
        # Configure mock dialog to change step to 2.0 (larger step)
        mock_dialog.get_values.return_value = (0.0, 10.0, 2.0)
        
        # Act - Change step from 0.5 to 2.0
        widget.open_adjust_dialog()
        
        # Assert - Value should be aligned to nearest 2.0 step (4.0)
        assert widget.step == 2.0
        assert widget.value == 4.0
        
        # Configure mock dialog to change step to very small value
        mock_dialog.get_values.return_value = (0.0, 10.0, 0.001)
        
        # Act - Change step from 2.0 to 0.001
        widget.open_adjust_dialog()
        
        # Assert - Value should remain at 4.0
        assert widget.step == 0.001
        assert widget.value == 4.0
        
        # Update value to a very precise number
        widget.set_value(4.002)
        assert abs(widget.value - 4.002) < 0.0001

    def test_step_change_does_not_trigger_value_change(self, monkeypatch, qtbot_extended):
        """
        Test that changing step size does not trigger a value change signal.
        
        Verifies:
        - Changing step size doesn't emit valueChanged signal
        - Value is only reported as changed programmatically via logs
        - After step change, user changes still emit valueChanged
        """
        # Arrange - Create widget with initial parameters
        widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "step": 1.0, "initial": 5.0})
        qtbot_extended.addWidget(widget)
        
        # Setup signal spy
        signal_spy = MagicMock()
        widget.register_callback(signal_spy)
        
        # Configure mock dialog
        mock_dialog = MagicMock()
        mock_dialog.exec_.return_value = True
        mock_dialog.get_values.return_value = (0.0, 10.0, 0.5)
        monkeypatch.setattr('pyqt_live_tuner.parameter_widgets.adjust_dialog.AdjustDialog', 
                            lambda *args, **kwargs: mock_dialog)
        
        # Act - Change step from 1.0 to 0.5
        widget.open_adjust_dialog()
        
        # Assert - No value change signal should be emitted
        signal_spy.assert_not_called()
        
        # Act - Now change value via spinbox
        widget.on_spinbox_changed(6.0)
        
        # Assert - Value change signal should be emitted
        signal_spy.assert_called_with("Test", 6.0)

    def test_step_change_extreme_values(self, monkeypatch, qapp):
        """
        Test step changes with extreme values to ensure stability.
        
        Verifies:
        - Changing from very large to very small step works correctly
        - Changing from very small to very large step works correctly
        - Value alignment works correctly with extreme step changes
        """
        # Arrange - Create widget with initial parameters
        widget = FloatParameterWidget("Test", {"min": 0, "max": 1000, "step": 100, "initial": 300})
        
        # Mock the dialog
        mock_dialog = MagicMock()
        mock_dialog.exec_.return_value = True
        
        # Patching
        monkeypatch.setattr('pyqt_live_tuner.parameter_widgets.adjust_dialog.AdjustDialog', 
                            lambda *args, **kwargs: mock_dialog)
        
        # Act - Change from very large (100) to very small step (0.001)
        mock_dialog.get_values.return_value = (0.0, 1000.0, 0.001)
        widget.open_adjust_dialog()
        
        # Assert
        assert widget.step == 0.001
        assert widget.value == 300.0
        
        # Update to a precise value
        widget.set_value(300.005)
        assert abs(widget.value - 300.005) < 0.0001
        
        # Act - Change from very small (0.001) to very large step (250)
        mock_dialog.get_values.return_value = (0.0, 1000.0, 250)
        widget.open_adjust_dialog()
        
        # Assert - Should align to nearest 250 step (250 or 500)
        assert widget.step == 250
        assert widget.value == 250.0 or widget.value == 500.0

    def test_integration_ui_interaction(self, qtbot_extended):
        """
        Integration test for user interaction with the widget.
        
        Verifies:
        - User can change values with spinbox and slider
        - Values are correctly synchronized between spinbox and slider
        - Value change callbacks are triggered correctly
        """
        # Arrange
        widget = FloatParameterWidget("Test", {"min": 0, "max": 10, "step": 0.5, "initial": 5.0})
        qtbot_extended.addWidget(widget)
        
        # Mock callback function
        callback = MagicMock()
        widget.register_callback(callback)
        
        # Act - Change via spinbox
        widget.spinbox.setValue(7.5)
        
        # Assert
        assert widget.value == 7.5
        assert widget.slider.value() == 15  # (7.5 - 0) / 0.5 = 15 steps
        callback.assert_called_with("Test", 7.5)
        
        # Reset mock
        callback.reset_mock()
        
        # Act - Change via slider
        widget.slider.setValue(10)  # Should be 5.0
        
        # Need to manually trigger slider release since programmatic changes don't
        widget.on_slider_released()
        
        # Assert
        assert widget.value == 5.0
        assert widget.spinbox.value() == 5.0
        callback.assert_called_with("Test", 5.0)