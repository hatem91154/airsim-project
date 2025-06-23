from PyQt5.QtWidgets import QLabel, QDoubleSpinBox, QSlider, QPushButton
from PyQt5.QtCore import Qt
from typing import Callable, Optional

from pyqt_live_tuner.logger import logger
from .parameter_widget import ParameterWidget
from .adjust_dialog import AdjustDialog


class FloatParameterWidget(ParameterWidget):
    """
    Float parameter widget with:
    - Spin box control
    - Optional slider
    - Adjustable min/max/step via pop-up dialog
    
    Attributes:
        name (str): Display name of the parameter
        value (float): Current parameter value
        min_val (float): Minimum allowed value
        max_val (float): Maximum allowed value
        step (float): Step size for incremental changes
        _decimal_places (int): Number of decimal places to display
        _updating_controls (bool): Flag to prevent recursive updates
    """

    def __init__(self, name: str = "Unnamed", config: Optional[dict] = None) -> None:
        """Initialize the float parameter widget.
        
        Args:
            name: Display name of the parameter
            config: Configuration dictionary with optional keys:
                - min: Minimum value (default: 0.0)
                - max: Maximum value (default: 1.0)
                - step: Step size (default: 0.01)
                - initial: Initial value (default: 0.0)
                - decimal_places: Number of decimal places (default: 3)
        """
        super().__init__(name, config)
        config = config or {}

        self.min_val = config.get("min", 0.0)
        self.max_val = config.get("max", 1.0)
        self.step = config.get("step", 0.01)
        self.value = config.get("initial", 0.0)
        self._decimal_places = config.get("decimal_places", 3)
        self._updating_controls = False  # Flag to prevent recursive updates

        self.label = QLabel(f"{self.name}:")

        self.spinbox = QDoubleSpinBox()
        self._configure_spinbox()
        
        self.slider = QSlider(Qt.Horizontal)
        self._configure_slider()

        self.adjust_button = QPushButton("⚙")
        self.adjust_button.setFixedWidth(30)
        self.adjust_button.setToolTip("Adjust min, max, step")
        self.adjust_button.clicked.connect(self._open_adjust_dialog)

        layout = self.layout
        layout.addWidget(self.label)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinbox)
        layout.addWidget(self.adjust_button)

        logger.debug(f"FloatParameterWidget created: {self.name} [{self.min_val}–{self.max_val}]")
    
    def _configure_spinbox(self):
        """Configure or reconfigure the spinbox with current settings.
        
        Sets up the spinbox's range, step size, decimal places, and connects signals.
        Disconnects any existing signal connections first to prevent unwanted triggers.
        """
        self.spinbox.setRange(self.min_val, self.max_val)
        self.spinbox.setSingleStep(self.step)
        self.spinbox.setDecimals(self._decimal_places)
        self.spinbox.setValue(self.value)
        
        # Disconnect any existing connections
        try:
            self.spinbox.valueChanged.disconnect()
        except:
            pass  # No connections to disconnect
            
        # Connect the signal
        self.spinbox.valueChanged.connect(self._on_spinbox_changed)
        self.spinbox.setAlignment(Qt.AlignCenter)
    
    def _configure_slider(self):
        """Configure or reconfigure the slider with current settings.
        
        Sets up the slider's range based on min, max, and step values,
        and positions the slider at the current value. Disconnects existing
        signal connections first to prevent unwanted triggers.
        """
        self.slider.setMinimum(0)
        steps = int((self.max_val - self.min_val) / self.step)
        self.slider.setMaximum(max(1, steps))
        
        # Set current slider position based on value
        position = int(round((self.value - self.min_val) / self.step))
        position = max(0, min(position, self.slider.maximum()))
        self.slider.setValue(position)
        
        # Disconnect any existing connections
        try:
            self.slider.valueChanged.disconnect()
            self.slider.sliderReleased.disconnect()
        except:
            pass  # No connections to disconnect
        
        # Connect the signals
        self.slider.valueChanged.connect(self._on_slider_changed)
        self.slider.sliderReleased.connect(lambda: self.emit_value_changed(self.value))

    def _block_all_signals(self, block=True):
        """Block or unblock signals from all controls to prevent unwanted updates.
        
        Args:
            block: True to block signals, False to unblock
        """
        self._updating_controls = block
        self.slider.blockSignals(block)
        self.spinbox.blockSignals(block)

    def _on_spinbox_changed(self, value: float):
        """Handle spinbox value change.
        
        Updates the value and syncs the slider position when the spinbox value changes.
        Emits the valueChanged signal to notify listeners of the change.
        
        Args:
            value: The new value from the spinbox
        """
        if self._updating_controls:
            return
            
        if abs(value - self.value) >= 1e-6:
            self.value = value
            self._sync_slider()
            logger.debug(f"[{self.name}] SpinBox changed → {value}")
            self.emit_value_changed(value)

    def _on_slider_changed(self, slider_val: int):
        """Handle slider value change.
        
        Updates the value and spinbox when the slider position changes.
        Does not emit the valueChanged signal (that happens on slider release).
        
        Args:
            slider_val: The new slider position
        """
        if self._updating_controls:
            return
            
        value = self._slider_position_to_value(slider_val)
        if abs(value - self.value) >= 1e-6:
            self.value = value
            
            # Update spinbox without triggering its valueChanged signal
            self._block_all_signals(True)
            self.spinbox.setValue(value)
            self._block_all_signals(False)
            
            logger.debug(f"[{self.name}] Slider changed → {value}")
            # Signal is emitted on sliderReleased instead

    def _slider_position_to_value(self, position: int) -> float:
        """Convert slider position to actual value based on min, max, and step.
        
        Args:
            position: Slider position (integer)
            
        Returns:
            The corresponding parameter value
        """
        value = self.min_val + position * self.step
        # Make sure we don't exceed max_val due to floating point errors
        return min(value, self.max_val)

    def _sync_slider(self):
        """Sync slider position to the current value without triggering callbacks.
        
        Calculates the appropriate slider position based on the current value 
        and updates the slider without triggering change events.
        """
        if self._updating_controls:
            return
            
        # Calculate slider position based on current value
        position = int(round((self.value - self.min_val) / self.step))
        
        # Ensure position is within valid range
        position = max(0, min(position, self.slider.maximum()))
        
        # Update slider without triggering its valueChanged signal
        self._block_all_signals(True)
        self.slider.setValue(position)
        self._block_all_signals(False)

    def _open_adjust_dialog(self):
        """Open a dialog to adjust min, max, and step values.
        
        Shows a dialog where the user can modify the parameter's range and step size.
        When changes are applied, maintains the relative position of the current value
        within the new range, preventing unwanted jumps in the slider position.
        """
        dialog = AdjustDialog(self.min_val, self.max_val, self.step)
        if dialog.exec_():
            new_min, new_max, new_step = dialog.get_values()
            if new_min >= new_max or new_step <= 0:
                logger.warning(f"[{self.name}] Invalid adjustment values")
                return

            # Store the current value to preserve after adjustment
            current_value = self.value
            
            # Log changes
            if new_min != self.min_val:
                logger.info(f"[{self.name}] Min changed: {self.min_val} → {new_min}")
            if new_max != self.max_val:
                logger.info(f"[{self.name}] Max changed: {self.max_val} → {new_max}")
            if new_step != self.step:
                logger.info(f"[{self.name}] Step changed: {self.step} → {new_step}")
                
            # Complete signal blockage - disconnect all signals
            self._block_all_signals(True)
            
            # Update parameters
            self.min_val = new_min
            self.max_val = new_max
            self.step = new_step
            
            # Snap the current value to the closest valid value with the new step
            clamped_value = max(self.min_val, min(current_value, self.max_val))
            # steps = round((clamped_value - self.min_val) / self.step)
            # new_value = self.min_val + steps * self.step
            # new_value = min(new_value, self.max_val)  # Protect against floating-point errors
            self.value = clamped_value
            
            # Completely reconfigure the widgets - this avoids any slider jumping issues
            self._configure_spinbox()
            self._configure_slider()
            
            # Unblock signals after all updates are complete
            self._block_all_signals(False)
            
            logger.debug(f"[{self.name}] Value set programmatically → {clamped_value}")

    def set_value(self, value: float) -> None:
        """Set the parameter value programmatically.
        
        Updates the widget's value and UI controls without triggering change events.
        The value is clamped to the valid range and aligned to the nearest step.
        
        Args:
            value: The new value to set
        """
        clamped = max(self.min_val, min(value, self.max_val))
        
        if abs(clamped - self.value) >= 1e-6:
            # Block signals to prevent callbacks during update
            self._block_all_signals(True)
            
            self.value = clamped
            
            self._configure_spinbox()
            self._configure_slider()

            # Unblock signals after all updates are complete
            self._block_all_signals(False)
            
            logger.debug(f"[{self.name}] Value set programmatically → {clamped}")

    def get_value(self) -> float:
        """Get the current parameter value.
        
        Returns:
            The current value of the parameter
        """
        return self.value

    def register_callback(self, callback: Callable[[str, float], None]) -> None:
        """Register a callback to be called when the value changes.
        
        Args:
            callback: Function to call when value changes, with signature:
                     callback(parameter_name, parameter_value)
        """
        self.valueChanged.connect(callback)
        logger.debug(f"[{self.name}] Callback registered: {callback}")
