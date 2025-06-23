#!/usr/bin/env python3
"""
Comprehensive example demonstrating all features of the pyqt_live_tuner library.

This example includes:
- All parameter types (Float, Bool, String, Action, Dropdown, Joystick)
- Parameter groups and linked parameter groups
- Parameter panels and config panels
- File handling for saving/loading parameter values

Run this file directly to see the demo in action.
"""

import os
import sys
import math
from PyQt5.QtWidgets import QMessageBox, QVBoxLayout, QLabel, QWidget
from PyQt5.QtCore import QTimer

# Import all components from the pyqt_live_tuner library
from pyqt_live_tuner import (
    # Core components
    LiveTunerApp, MainWindow, FileHandler,
    
    # Parameter types
    Parameter, FloatParameter, BoolParameter, StringParameter,
    ActionParameter, DropdownParameter, JoystickParameter,
    
    # Groups
    ParameterGroup, LinkedParameterGroup,
    
    # Panels
    ParameterPanel, ConfigPanel
)


class ComprehensiveExample:
    """Example application demonstrating all features of pyqt_live_tuner."""
    
    def __init__(self):
        """Initialize the example application."""
        # Create the main application
        self.app = LiveTunerApp(title="PyQt Live Tuner - Comprehensive Example", use_dark_theme=True)
        
        # Create file handler for saving/loading parameters
        self.file_handler = FileHandler()
        # Set default save path to a file in the current directory
        default_save_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "example_config.json")
        self.file_handler.set_save_path(default_save_path)
        
        # Set up the main window
        self.main_window = self.app.main_window
        self.main_window.resize(1000, 800)  # Set a comfortable size
        
        # Add status bar functionality to MainWindow
        # This adds a custom method to show status messages
        self.setup_status_bar()
        
        # Create example panels
        self.create_basic_parameters_panel()
        self.create_advanced_parameters_panel()
        self.create_animation_panel()
        self.create_config_panel()
        
        # Set up parameter callbacks
        self.setup_callbacks()
        
        
        # Set up animation timer
        self.animation_timer = QTimer()
        # self.animation_timer.timeout.connect(self.update_animation)
        # self.animation_timer.start(50)  # 20 FPS
        # self.animation_time = 0.0
        
    def setup_status_bar(self):
        """Set up status bar functionality for the main window.
        
        This adds a custom set_status_message method to the MainWindow instance
        that can be used to display temporary status messages.
        """
        from PyQt5.QtCore import QTimer
        
        # Create status bar
        status_bar = self.main_window.statusBar()
        
        # Add a custom method to the main window for displaying status messages
        def set_status_message(message, timeout=0):
            """Display a message in the status bar.
            
            Args:
                message: Message to display
                timeout: Time in milliseconds before the message is cleared (0 = no timeout)
            """
            status_bar.showMessage(message)
            if timeout > 0:
                QTimer.singleShot(timeout, lambda: status_bar.clearMessage())
                
        # Add the method to the main window instance
        self.main_window.set_status_message = set_status_message
        
        # Show an initial welcome message
        self.main_window.set_status_message("Welcome to PyQt Live Tuner Example!", 3000)
        
    def create_basic_parameters_panel(self):
        """Create a panel with basic parameter types."""
        panel = ParameterPanel()
        
        # Create a group for numeric parameters
        numeric_group = ParameterGroup("Numeric Parameters")
        
        # Add float parameters with different configurations
        self.basic_float = FloatParameter("Basic Float", {
            "min": 0.0, 
            "max": 1.0, 
            "step": 0.01, 
            "initial": 0.5
        })
        
        self.wide_range_float = FloatParameter("Wide Range Float", {
            "min": -100.0, 
            "max": 100.0, 
            "step": 0.5, 
            "initial": 25.0, 
            "decimal_places": 1
        })
        
        self.precise_float = FloatParameter("Precise Float", {
            "min": 0.0, 
            "max": 0.1, 
            "step": 0.0001, 
            "initial": 0.05, 
            "decimal_places": 5
        })
        
        # Add bool parameters
        self.simple_bool = BoolParameter("Simple Boolean", {"initial": True})
        self.toggle_bool = BoolParameter("Toggle Feature", {"initial": False})
        
        # Add parameters to the group
        numeric_group.add_parameter(self.basic_float)
        numeric_group.add_parameter(self.wide_range_float)
        numeric_group.add_parameter(self.precise_float)
        numeric_group.add_parameter(self.simple_bool)
        numeric_group.add_parameter(self.toggle_bool)
        
        # Create a group for text parameters
        text_group = ParameterGroup("Text Parameters")
        
        # Add string parameter
        self.string_param = StringParameter("Text Input", {
            "initial": "Hello, World!",
            "placeholder": "Enter some text..."
        })
        
        # Add dropdown parameter
        self.dropdown_param = DropdownParameter("Selection", {
            "options": ["Option 1", "Option 2", "Option 3", "Custom Option"],
            "initial": "Option 1",
            "allow_custom": True
        })
        
        # Add parameters to the group
        text_group.add_parameter(self.string_param)
        text_group.add_parameter(self.dropdown_param)
        
        # Create a group for action parameters
        action_group = ParameterGroup("Actions")
        
        # Add action parameters
        self.action1 = ActionParameter("Show Message", {
            "label": "Click Me!",
            "callback": self.show_message
        })
        
        self.action2 = ActionParameter("Reset Values", {
            "label": "Reset",
            "callback": self.reset_basic_values
        })
        
        # Add parameters to the group
        action_group.add_parameter(self.action1)
        action_group.add_parameter(self.action2)
        
        # Add all groups to the panel
        panel.add_group(numeric_group)
        panel.add_group(text_group)
        panel.add_group(action_group)
        
        # Add the panel to the main window with a title
        self.main_window.add_panel(panel, (0, 0), "Basic Parameters")
        
    def create_advanced_parameters_panel(self):
        """Create a panel with advanced parameter types and linked parameters."""
        panel = ParameterPanel()
        
        # Create a linked parameter group for RGB color
        color_group = LinkedParameterGroup("RGB Color")
        
        # Add RGB parameters
        self.red_param = FloatParameter("Red", {
            "min": 0.0, 
            "max": 1.0, 
            "step": 0.01, 
            "initial": 1.0
        })
        
        self.green_param = FloatParameter("Green", {
            "min": 0.0, 
            "max": 1.0, 
            "step": 0.01, 
            "initial": 0.0
        })
        
        self.blue_param = FloatParameter("Blue", {
            "min": 0.0, 
            "max": 1.0, 
            "step": 0.01, 
            "initial": 0.0
        })
        
        # Add parameters to the linked group with a callback to update the color preview
        color_group.add_parameter(self.red_param)
        color_group.add_parameter(self.green_param)
        color_group.add_parameter(self.blue_param)
        color_group.set_callback(self.update_color_preview)
        
        # Create joystick parameters with different configurations
        joystick_group = ParameterGroup("Joystick Controls")
        
        # Standard joystick with circular dead zone
        self.joystick_circular = JoystickParameter("Circular Dead Zone", {
            "x_initial": 0.0,
            "y_initial": 0.0,
            "return_to_center": True,
            "dead_zone": 0.15,           # 15% circular dead zone
            "update_frequency": 10       # 10 updates per second
        })
        
        # X-axis focused joystick with X-axis dead zone (good for throttle)
        self.joystick_x_axis = JoystickParameter("X-Axis Dead Zone", {
            "x_initial": 0.0,
            "y_initial": 0.0,
            "return_to_center": True,
            "dead_zone_x": 0.1,          # 10% X-axis dead zone
            "dead_zone_y": 0.3,          # 30% Y-axis dead zone
            "update_frequency": 10       
        })
        
        # Y-axis focused joystick with Y-axis dead zone
        self.joystick_y_axis = JoystickParameter("Y-Axis Dead Zone", {
            "x_initial": 0.0,
            "y_initial": 0.0,
            "return_to_center": True,
            "dead_zone_x": 0.3,          # 30% X-axis dead zone
            "dead_zone_y": 0.1,          # 10% Y-axis dead zone
            "update_frequency": 10       
        })
        
        # Combined dead zones
        self.joystick_combined = JoystickParameter("Combined Dead Zones", {
            "x_initial": 0.0,
            "y_initial": 0.0,
            "return_to_center": True,
            "dead_zone": 0.1,            # 10% circular dead zone
            "dead_zone_x": 0.2,          # 20% X-axis dead zone
            "dead_zone_y": 0.2,          # 20% Y-axis dead zone
            "update_frequency": 10       
        })
        
        # Add joysticks to the group
        joystick_group.add_parameter(self.joystick_circular)
        joystick_group.add_parameter(self.joystick_x_axis)
        joystick_group.add_parameter(self.joystick_y_axis)
        joystick_group.add_parameter(self.joystick_combined)
        
        # Create a color preview widget
        self.color_preview = QWidget()
        self.color_preview.setMinimumHeight(50)
        self.color_preview.setStyleSheet("background-color: rgb(255, 0, 0);")
        
        # Create a layout for the color preview
        color_preview_widget = QWidget()
        color_preview_layout = QVBoxLayout(color_preview_widget)
        color_preview_layout.addWidget(QLabel("Color Preview:"))
        color_preview_layout.addWidget(self.color_preview)
        
        # Add groups and widgets to the panel
        panel.add_group(color_group)
        panel.add_group(joystick_group)
        panel.add_widget(color_preview_widget)
        
        # Add the panel to the main window with a title
        self.main_window.add_panel(panel, (0, 1), "Advanced Parameters")
          
    def create_animation_panel(self):
        """Create a panel with animation controls."""
        panel = ParameterPanel()
        
        # Create animation controls
        animation_controls = ParameterGroup("Animation Controls")
        
        self.animation_speed = FloatParameter("Speed", {
            "min": 0.1,
            "max": 5.0,
            "step": 0.1,
            "initial": 1.0
        })
        
        self.animation_amplitude = FloatParameter("Amplitude", {
            "min": 0.0,
            "max": 10.0,
            "step": 0.1,
            "initial": 1.0
        })
        
        self.animation_enabled = BoolParameter("Enable Animation", {
            "initial": True
        })
        
        # Add controls to the group
        animation_controls.add_parameter(self.animation_speed)
        animation_controls.add_parameter(self.animation_amplitude)
        animation_controls.add_parameter(self.animation_enabled)
        
        # Create output parameters that will be animated
        animation_outputs = ParameterGroup("Animation Output")
        
        self.sine_output = FloatParameter("Sine Wave", {
            "min": -10.0,
            "max": 10.0,
            "step": 0.01,
            "initial": 0.0
        })
        
        self.cosine_output = FloatParameter("Cosine Wave", {
            "min": -10.0,
            "max": 10.0,
            "step": 0.01,
            "initial": 0.0
        })
        
        self.combined_output = FloatParameter("Combined", {
            "min": -10.0,
            "max": 10.0,
            "step": 0.01,
            "initial": 0.0
        })
        
        # Add outputs to the group
        animation_outputs.add_parameter(self.sine_output)
        animation_outputs.add_parameter(self.cosine_output)
        animation_outputs.add_parameter(self.combined_output)
        
        # Add groups to the panel
        panel.add_group(animation_controls)
        panel.add_group(animation_outputs)
        
        # Add the panel to the main window with a title
        self.main_window.add_panel(panel, (1, 1), "Animation")
        
    def create_config_panel(self):
        """Create a configuration panel."""
        panel = ConfigPanel()
        
        # Add configuration options
        self.auto_save = BoolParameter("Auto Save", {
            "initial": False
        })
        
        self.refresh_rate = FloatParameter("Refresh Rate (Hz)", {
            "min": 1.0,
            "max": 60.0,
            "step": 1.0,
            "initial": 20.0
        })
        
        self.dark_mode = BoolParameter("Dark Mode", {
            "initial": True
        })
        
        self.language = DropdownParameter("Language", {
            "options": ["English", "Spanish", "French", "German", "Japanese"],
            "initial": "English"
        })
        
        # Add parameters to the panel
        panel.add_widget(self.auto_save)
        panel.add_widget(self.refresh_rate)
        panel.add_widget(self.dark_mode)
        panel.add_widget(self.language)
        
        # Add the panel to the main window with a title
        self.main_window.add_panel(panel, (1, 0), "Configuration")
        
    def setup_callbacks(self):
        """Set up callbacks for parameters."""
        # Register callbacks for the joystick
        # self.joystick_param.register_callback(self.on_joystick_moved)
        
        # # Register callbacks for toggle parameters
        # self.toggle_bool.register_callback(self.on_toggle_changed)
        # self.animation_enabled.register_callback(self.on_animation_enabled_changed)
        
        # # Register callbacks for dropdown
        # self.dropdown_param.register_callback(self.on_dropdown_changed)
        
        # # Register callbacks for dark mode toggle
        # self.dark_mode.register_callback(self.on_dark_mode_changed)
        
    def on_joystick_moved(self, name, value):
        """Handle joystick movement."""
        x, y = value
        message = f"Joystick position: X={x:.2f}, Y={y:.2f}"
        self.main_window.set_status_message(message, 2000)
        
    def on_toggle_changed(self, name, value):
        """Handle toggle change."""
        status = "enabled" if value else "disabled"
        self.main_window.set_status_message(f"Feature {status}", 2000)
        
    def on_dropdown_changed(self, name, value):
        """Handle dropdown selection change."""
        self.main_window.set_status_message(f"Selected: {value}", 2000)
        
    def on_animation_enabled_changed(self, name, value):
        """Handle animation enabled toggle."""
        if value:
            self.animation_timer.start(50)
            self.main_window.set_status_message("Animation started", 2000)
        else:
            self.animation_timer.stop()
            self.main_window.set_status_message("Animation stopped", 2000)
            
    def on_dark_mode_changed(self, name, value):
        """Handle dark mode toggle."""
        # Note: In a real application, you would implement theme switching here
        self.main_window.set_status_message(f"Dark mode {'enabled' if value else 'disabled'}", 2000)
        
    def update_animation(self):
        """Update animation parameters."""
        if not self.animation_enabled.get_value():
            return
            
        # Update animation time
        speed = self.animation_speed.get_value()
        self.animation_time += 0.05 * speed
        
        # Calculate new values
        amplitude = self.animation_amplitude.get_value()
        sine_value = amplitude * math.sin(self.animation_time)
        cosine_value = amplitude * math.cos(self.animation_time)
        combined_value = sine_value + cosine_value
        
        # Update output parameters
        self.sine_output.set_value(sine_value)
        self.cosine_output.set_value(cosine_value)
        self.combined_output.set_value(combined_value)
        
    def update_color_preview(self, group_name, values):
        """Update the color preview widget based on RGB values."""
        r = int(values["Red"] * 255)
        g = int(values["Green"] * 255)
        b = int(values["Blue"] * 255)
        self.color_preview.setStyleSheet(f"background-color: rgb({r}, {g}, {b});")
        
    def update_model_view(self, name, value):
        """Update the 3D model view based on rotation and zoom parameters."""
        # In a real application, this would update the 3D model view
        # But for this example, we'll just show a status message
        rotation_x = self.rotation_x.get_value()
        rotation_y = self.rotation_y.get_value()
        zoom = self.zoom.get_value()
        self.main_window.set_status_message(f"Model view updated: RotX={rotation_x}, RotY={rotation_y}, Zoom={zoom}", 2000)
        
        # If we had a real 3D model, we would update it here
        if hasattr(self, 'model_param'):
            # self.model_param.set_rotation(rotation_x, rotation_y, 0)
            # self.model_param.set_zoom(zoom)
            pass
        
    def show_message(self):
        """Show a message dialog when the action button is clicked."""
        QMessageBox.information(
            self.main_window,
            "Message",
            "This is an example message triggered by the action parameter!"
        )
        
    def reset_basic_values(self):
        """Reset basic parameters to their initial values."""
        self.basic_float.set_value(0.5)
        self.wide_range_float.set_value(25.0)
        self.precise_float.set_value(0.05)
        self.simple_bool.set_value(True)
        self.toggle_bool.set_value(False)
        self.string_param.set_value("Hello, World!")
        self.dropdown_param.set_value("Option 1")
        
        self.main_window.set_status_message("Basic values reset to defaults", 2000)
        
    def run(self):
        """Run the application."""
        return self.app.run()


def main():
    """Main entry point for the example application."""
    example = ComprehensiveExample()
    return example.run()


if __name__ == "__main__":
    sys.exit(main())