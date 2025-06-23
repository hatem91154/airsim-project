#!/usr/bin/env python3
"""
Rotation Parameter Example - Demonstrates the RotationParameter widget.
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

class RotationParameterExample(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Rotation Parameter Example")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create rotation parameter group
        rotation_group = QGroupBox("Rotation Parameters")
        rotation_layout = QVBoxLayout(rotation_group)
        
        # Parameter containers
        param_layout = QHBoxLayout()
        
        # Standard rotation parameter
        standard_container = QGroupBox("Standard Rotation")
        standard_layout = QVBoxLayout(standard_container)
        self.standard_rotation = RotationParameter("Angle", {
            "initial": 45.0,
            "size": 200
        })
        self.standard_rotation.register_callback(self.on_standard_rotation_changed)
        standard_layout.addWidget(self.standard_rotation)
        self.standard_value_label = QLabel("Value: 45.0°")
        standard_layout.addWidget(self.standard_value_label)
        param_layout.addWidget(standard_container)
        
        # Rotation with snapping
        snapping_container = QGroupBox("Rotation with Snapping")
        snapping_layout = QVBoxLayout(snapping_container)
        self.snapping_rotation = RotationParameter("Angle", {
            "initial": 0.0,
            "size": 200,
            "snap": True,
            "snap_angles": [0, 45, 90, 135, 180, 225, 270, 315],
            "snap_threshold": 10.0
        })
        self.snapping_rotation.register_callback(self.on_snapping_rotation_changed)
        snapping_layout.addWidget(self.snapping_rotation)
        self.snapping_value_label = QLabel("Value: 0.0°")
        snapping_layout.addWidget(self.snapping_value_label)
        param_layout.addWidget(snapping_container)
        
        # Add parameter containers to rotation group
        rotation_layout.addLayout(param_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Create animation button
        animate_btn = QPushButton("Animate Rotation")
        animate_btn.clicked.connect(self.toggle_animation)
        button_layout.addWidget(animate_btn)
        
        # Reset button
        reset_btn = QPushButton("Reset Rotations")
        reset_btn.clicked.connect(self.reset_rotations)
        button_layout.addWidget(reset_btn)
        
        # Set to 90° button
        set_90_btn = QPushButton("Set to 90°")
        set_90_btn.clicked.connect(lambda: self.set_rotations(90))
        button_layout.addWidget(set_90_btn)
        
        # Set to 180° button
        set_180_btn = QPushButton("Set to 180°")
        set_180_btn.clicked.connect(lambda: self.set_rotations(180))
        button_layout.addWidget(set_180_btn)
        
        # Set to 270° button
        set_270_btn = QPushButton("Set to 270°")
        set_270_btn.clicked.connect(lambda: self.set_rotations(270))
        button_layout.addWidget(set_270_btn)
        
        # Add layouts to main layout
        main_layout.addWidget(rotation_group)
        main_layout.addLayout(button_layout)
        
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
    
    def toggle_animation(self):
        """Toggle rotation animation on/off."""
        self.animation_active = not self.animation_active
        
        if self.animation_active:
            self.animation_timer.start(30)  # Update approximately 30 times per second
        else:
            self.animation_timer.stop()
    
    def update_animation(self):
        """Update animation frame for rotating dials."""
        self.animation_angle = (self.animation_angle + 2.0) % 360.0
        
        # Update both rotation parameters
        self.standard_rotation.set_value(self.animation_angle)
        self.snapping_rotation.set_value(self.animation_angle)
    
    def reset_rotations(self):
        """Reset rotations to initial values."""
        self.standard_rotation.set_value(45.0)
        self.snapping_rotation.set_value(0.0)
    
    def set_rotations(self, angle):
        """Set both rotations to the specified angle."""
        self.standard_rotation.set_value(angle)
        self.snapping_rotation.set_value(angle)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RotationParameterExample()
    window.show()
    sys.exit(app.exec_())