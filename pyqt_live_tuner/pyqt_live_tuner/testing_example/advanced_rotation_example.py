#!/usr/bin/env python3
"""
Advanced Rotation Parameter Example - Demonstrates all features of the RotationParameter widget.
"""

import sys
import os
import math
import numpy as np

# Add parent directory to path to ensure we can import from pyqt_live_tuner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, 
    QPushButton, QHBoxLayout, QLabel, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer

from pyqt_live_tuner.parameters.rotation_parameter import RotationParameter

class AdvancedRotationExample(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Advanced Rotation Parameter Example")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create rotation parameters grid layout
        params_layout = QHBoxLayout()
        
        # 1. Standard rotation parameter
        standard_container = QGroupBox("Standard Rotation")
        standard_layout = QVBoxLayout(standard_container)
        self.standard_rotation = RotationParameter("Angle", {
            "initial": 45.0,
            "size": 180
        })
        self.standard_rotation.register_callback(self.on_standard_rotation_changed)
        standard_layout.addWidget(self.standard_rotation)
        self.standard_value_label = QLabel("Value: 45.0°")
        standard_layout.addWidget(self.standard_value_label)
        params_layout.addWidget(standard_container)
        
        # 2. Rotation with snapping
        snapping_container = QGroupBox("Rotation with Snapping")
        snapping_layout = QVBoxLayout(snapping_container)
        self.snapping_rotation = RotationParameter("Angle", {
            "initial": 0.0,
            "size": 180,
            "snap": True,
            "snap_angles": [0, 45, 90, 135, 180, 225, 270, 315],
            "snap_threshold": 10.0
        })
        self.snapping_rotation.register_callback(self.on_snapping_rotation_changed)
        snapping_layout.addWidget(self.snapping_rotation)
        self.snapping_value_label = QLabel("Value: 0.0°")
        snapping_layout.addWidget(self.snapping_value_label)
        params_layout.addWidget(snapping_container)
        
        # 3. Rotation with different zero orientation (right)
        right_zero_container = QGroupBox("Right-Oriented (Zero at Right)")
        right_zero_layout = QVBoxLayout(right_zero_container)
        self.right_zero_rotation = RotationParameter("Angle", {
            "initial": 90.0,
            "size": 180,
            "zero_orientation": "right"
        })
        self.right_zero_rotation.register_callback(self.on_right_zero_rotation_changed)
        right_zero_layout.addWidget(self.right_zero_rotation)
        self.right_zero_value_label = QLabel("Value: 90.0°")
        right_zero_layout.addWidget(self.right_zero_value_label)
        params_layout.addWidget(right_zero_container)
        
        # Add first row to main layout
        main_layout.addLayout(params_layout)
        
        # Create second row
        params_layout2 = QHBoxLayout()
        
        # 4. Rotation with auto-return to origin
        auto_return_container = QGroupBox("Auto-Return to Origin")
        auto_return_layout = QVBoxLayout(auto_return_container)
        self.auto_return_rotation = RotationParameter("Angle", {
            "initial": 0.0,
            "size": 180,
            "auto_return": True,
            "zero_orientation": "top"
        })
        self.auto_return_rotation.register_callback(self.on_auto_return_rotation_changed)
        auto_return_layout.addWidget(self.auto_return_rotation)
        self.auto_return_value_label = QLabel("Value: 0.0°\nRelease to return to origin")
        self.auto_return_value_label.setAlignment(Qt.AlignCenter)
        auto_return_layout.addWidget(self.auto_return_value_label)
        params_layout2.addWidget(auto_return_container)
        
        # 5. Rotation with angle limits
        limited_container = QGroupBox("Limited Range (45° to 315°)")
        limited_layout = QVBoxLayout(limited_container)
        self.limited_rotation = RotationParameter("Angle", {
            "initial": 90.0,
            "size": 180,
            "min_angle": 45,
            "max_angle": 315
        })
        self.limited_rotation.register_callback(self.on_limited_rotation_changed)
        limited_layout.addWidget(self.limited_rotation)
        self.limited_value_label = QLabel("Value: 90.0°\nCannot rotate below 45° or above 315°")
        self.limited_value_label.setAlignment(Qt.AlignCenter)
        limited_layout.addWidget(self.limited_value_label)
        params_layout2.addWidget(limited_container)
        
        # 6. Rotation using -180 to 180 convention
        convention_container = QGroupBox("-180° to 180° Convention")
        convention_layout = QVBoxLayout(convention_container)
        self.convention_rotation = RotationParameter("Angle", {
            "initial": 0.0,
            "size": 180,
            "use_180_convention": True
        })
        self.convention_rotation.register_callback(self.on_convention_rotation_changed)
        convention_layout.addWidget(self.convention_rotation)
        self.convention_value_label = QLabel("Value: 0.0°\nDisplays as -180° to 180° instead of 0° to 359°")
        self.convention_value_label.setAlignment(Qt.AlignCenter)
        convention_layout.addWidget(self.convention_value_label)
        params_layout2.addWidget(convention_container)
        
        # Add second row to main layout
        main_layout.addLayout(params_layout2)
        
        # Button panel
        button_panel = QGroupBox("Control Panel")
        button_layout = QVBoxLayout(button_panel)
        
        # Button layout with multiple controls in a row
        control_layout = QHBoxLayout()
        
        # Animation toggle button
        self.animate_btn = QPushButton("Start Animation")
        self.animate_btn.clicked.connect(self.toggle_animation)
        control_layout.addWidget(self.animate_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset All Rotations")
        reset_btn.clicked.connect(self.reset_rotations)
        control_layout.addWidget(reset_btn)
        
        # Set to 90° button
        set_90_btn = QPushButton("Set All to 90°")
        set_90_btn.clicked.connect(lambda: self.set_all_rotations(90))
        control_layout.addWidget(set_90_btn)
        
        # Set to 180° button
        set_180_btn = QPushButton("Set All to 180°")
        set_180_btn.clicked.connect(lambda: self.set_all_rotations(180))
        control_layout.addWidget(set_180_btn)
        
        # Set to 270° button
        set_270_btn = QPushButton("Set All to 270°")
        set_270_btn.clicked.connect(lambda: self.set_all_rotations(270))
        control_layout.addWidget(set_270_btn)
        
        button_layout.addLayout(control_layout)
        
        # Detailed instructions
        instructions = QLabel(
            "Rotation Dial Controls:\n"
            "• Click and drag to rotate the dial\n"
            "• Use left/right arrow keys for precise adjustment (hold Shift for 15° steps)\n"
            "• Up arrow snaps to nearest 90° mark\n"
            "• Down arrow or Home key returns to origin\n"
            "• End key moves to opposite of origin\n\n"
            "Each dial demonstrates different configuration options."
        )
        instructions.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(instructions)
        
        main_layout.addWidget(button_panel)
        
        # Animation timer
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_active = False
        self.animation_angle = 0.0
        
        # Set central widget
        self.setCentralWidget(central_widget)
    
    def on_standard_rotation_changed(self, name, value):
        """Handle standard rotation parameter changes."""
        self.standard_value_label.setText(f"Value: {value:.1f}°")
    
    def on_snapping_rotation_changed(self, name, value):
        """Handle snapping rotation parameter changes."""
        self.snapping_value_label.setText(f"Value: {value:.1f}°")
    
    def on_right_zero_rotation_changed(self, name, value):
        """Handle right-zero rotation parameter changes."""
        display_angle = self.right_zero_rotation.rotation_dial.get_display_angle()
        self.right_zero_value_label.setText(f"Value: {value:.1f}°\nDisplay: {display_angle:.1f}°")
    
    def on_auto_return_rotation_changed(self, name, value):
        """Handle auto-return rotation parameter changes."""
        self.auto_return_value_label.setText(f"Value: {value:.1f}°\nRelease to return to origin")
    
    def on_limited_rotation_changed(self, name, value):
        """Handle limited range rotation parameter changes."""
        self.limited_value_label.setText(f"Value: {value:.1f}°\nLimited between 45° and 315°")
    
    def on_convention_rotation_changed(self, name, value):
        """Handle -180 to 180 convention rotation parameter changes."""
        display_angle = self.convention_rotation.rotation_dial.get_display_angle()
        self.convention_value_label.setText(f"Raw: {value:.1f}°\nDisplay: {display_angle:.1f}°")
    
    def toggle_animation(self):
        """Toggle rotation animation on/off."""
        self.animation_active = not self.animation_active
        
        if self.animation_active:
            self.animate_btn.setText("Stop Animation")
            self.animation_timer.start(30)  # Update approximately 30 times per second
        else:
            self.animate_btn.setText("Start Animation")
            self.animation_timer.stop()
    
    def update_animation(self):
        """Update animation frame for rotating dials."""
        self.animation_angle = (self.animation_angle + 2.0) % 360.0
        
        # Update all rotation parameters (some may be limited by constraints)
        self.standard_rotation.set_value(self.animation_angle)
        self.snapping_rotation.set_value(self.animation_angle)
        self.right_zero_rotation.set_value(self.animation_angle)
        self.auto_return_rotation.set_value(self.animation_angle)
        self.limited_rotation.set_value(self.animation_angle)
        self.convention_rotation.set_value(self.animation_angle)
    
    def reset_rotations(self):
        """Reset rotations to initial values."""
        self.standard_rotation.set_value(45.0)
        self.snapping_rotation.set_value(0.0)
        self.right_zero_rotation.set_value(90.0)
        self.auto_return_rotation.set_value(0.0)
        self.limited_rotation.set_value(90.0)
        self.convention_rotation.set_value(0.0)
    
    def set_all_rotations(self, angle):
        """Set all rotations to the specified angle."""
        self.standard_rotation.set_value(angle)
        self.snapping_rotation.set_value(angle)
        self.right_zero_rotation.set_value(angle)
        self.auto_return_rotation.set_value(angle)
        self.limited_rotation.set_value(angle)
        self.convention_rotation.set_value(angle)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AdvancedRotationExample()
    window.show()
    sys.exit(app.exec_())