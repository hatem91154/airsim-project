#!/usr/bin/env python3
"""
Cosys AirSim GUI - Graphical interface for AirSim using the pyqt_live_tuner library.
"""

import os
import sys
import time
import math
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QLabel, 
    QVBoxLayout,
    QGridLayout,
    QWidget, 
    QTextEdit, 
    QPushButton, 
    QHBoxLayout, 
    QGroupBox,
    QTabWidget
)

# import pysignal
from PyQt5.QtCore import pyqtSignal, QObject

import cosysairsim as airsim


# Import from pyqt_live_tuner library
from pyqt_live_tuner.app import LiveTunerApp
from pyqt_live_tuner.window import MainWindow
from pyqt_live_tuner.parameters import (
    ActionParameter, 
    StringParameter, 
    DropdownParameter,
    JoystickParameter,
    FloatParameter,
    BoolParameter
)
from pyqt_live_tuner.groups import ParameterGroup, LinkedParameterGroup
from pyqt_live_tuner.panels import ParameterPanel

class ButtonWithStatus(QWidget):
    """Button with status label."""

    clicked = pyqtSignal()

    def __init__(self, text):
        """Initialize the button with a status label."""
        super().__init__()
        
        layout = QHBoxLayout()
        margin = 0
        layout.setContentsMargins(margin, margin, margin, margin)  # Minimal margins
        layout.setSpacing(2)  # Minimal spacing
        self.setLayout(layout)
        
        self.button = QPushButton(text)
        self.button.setMaximumWidth(100)
        self.button.clicked.connect(self.clicked.emit)
        
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.button)
        layout.addWidget(self.status_label)

    def register_callback(self, callback):
        """Register a callback function for button click."""
        self.clicked.connect(callback)

    def set_status(self, status, color):
        """Set the status label text and color."""
        self.status_label.setText(status)
        self.status_label.setStyleSheet(f"color: {color}")


class AirSimGUI:
    """AirSim GUI using pyqt_live_tuner library."""

    def __init__(self):
        """Initialize the AirSim GUI."""
        # Create the LiveTunerApp
        self.app = LiveTunerApp("AirSim GUI")
        
        # Create the main window
        self.main_window = self.app.main_window
        
        # Initialize AirSim client if available
        self.client = airsim.MultirotorClient()
        self.vehicle_name = "SimpleFlight"
        self.camera_name = "0"
        self.is_connected = False
        self.recording = False  # Track recording state
        self.hover_active = False  # Track hover mode state
        
        # Set up the GUI
        self._setup_configuration_panel()
        # self._setup_action_panel()  # Re-enable action panel setup
        self._setup_camera_panel()  # Enable camera panel with integrated camera position controls
        # self._setup_environment_panel()

        # create Logger 
        logger_panel = QGroupBox("Log")
        # logger_panel.setMaximumHeight(200)
        logger_panel.setMinimumHeight(200)
        
        logger_layout = QVBoxLayout()
        
        self.logger = QTextEdit()
        
        self._logger_clearn_btn = QPushButton("Clear")
        self._logger_clearn_btn.clicked.connect(self.logger.clear)
        

        logger_layout.addWidget(self.logger)
        logger_layout.addWidget(self._logger_clearn_btn)

        logger_panel.setLayout(logger_layout)

        # Add panel to window
        self.main_window.add_panel(logger_panel, (1, 0), row_span=1, col_span=2)


        # Create a timer for updating the connection status
        self._connection_timer = QTimer()
        self._connection_timer.timeout.connect(self._update_connection_status)
        self._connection_timer.start(1000)

    def _setup_configuration_panel(self):
        """Set up the configuration panel."""
        # Create a parameter panel for configuration
        config_panel = QGroupBox("Configuration")
        config_layout = QVBoxLayout()
        # config_layout.setContentsMargins(0, 0, 0, 0)
        config_layout.setSpacing(2)

        config_panel.setLayout(config_layout)
        
        # Add connection button
        self._connect_btn = ButtonWithStatus("Connect")
        self._connect_btn.set_status("Not Connected", "red")
        self._connect_btn.clicked.connect(self._on_connect)
        config_layout.addWidget(self._connect_btn)
        
        # Add Enable API button
        self._enable_api_btn = ButtonWithStatus("Enable API")
        self._enable_api_btn.set_status("Disabled", "red")
        self._enable_api_btn.clicked.connect(self._on_enable_api)
        config_layout.addWidget(self._enable_api_btn)

        # Add vehicle name parameter with label in horizontal layout
        vehicle_layout = QHBoxLayout()
        vehicle_layout.setContentsMargins(1, 1, 1, 1)
        vehicle_layout.setSpacing(0)
        vehicle_label = QLabel("Vehicle Name:")
        vehicle_layout.addWidget(vehicle_label)
        
        self.vehicle_name = StringParameter("", {"initial": "SimpleFlight"})
        self.vehicle_name.register_callback(self._debug_callback)
        vehicle_layout.addWidget(self.vehicle_name)
        config_layout.addLayout(vehicle_layout)
        
        # Add camera name parameter with label in horizontal layout
        camera_layout = QHBoxLayout()
        camera_layout.setContentsMargins(1, 1, 1, 1)
        camera_layout.setSpacing(0)
        camera_label = QLabel("Camera Name:")
        camera_layout.addWidget(camera_label)
        
        self.camera_name_widget = StringParameter("", {"initial": "0"})
        self.camera_name_widget.register_callback(self._debug_callback)
        camera_layout.addWidget(self.camera_name_widget)
        config_layout.addLayout(camera_layout)
        
        # Add panel to window at position (0, 0)
        self.main_window.add_panel(config_panel, (0, 0))
    
    def _setup_camera_panel(self):
        """Set up the camera settings panel."""
        camera_panel = QGroupBox("Camera Settings")
        camera_layout = QVBoxLayout()
        camera_layout.setSpacing(5)
        camera_panel.setLayout(camera_layout)
        
        # Camera type selection
        cam_type_layout = QHBoxLayout()
        cam_type_label = QLabel("Camera Type:")
        cam_type_layout.addWidget(cam_type_label)
        
        self.cam_type = DropdownParameter("", {
            "options": ["Scene", "Depth", "Segmentation", "Normals", "DepthPlanar", "DepthPerspective", "DisparityNormalized", "OpticalFlow"],
            "initial": "Scene"
        })
        self.cam_type.register_callback(self._on_camera_type_changed)
        cam_type_layout.addWidget(self.cam_type)
        camera_layout.addLayout(cam_type_layout)
        
        # Camera FOV adjustment
        fov_layout = QHBoxLayout()
        fov_label = QLabel("FOV (degrees):")
        fov_layout.addWidget(fov_label)
        
        self.cam_fov = FloatParameter("", {
            "min": 10.0,
            "max": 120.0,
            "step": 1.0,
            "initial": 90.0
        })
        self.cam_fov.register_callback(self._on_camera_fov_changed)
        fov_layout.addWidget(self.cam_fov)
        camera_layout.addLayout(fov_layout)
        
        # Create tabs for different camera settings categories
        tabs = QTabWidget()
        
        # Tab 1: Position and Rotation
        position_tab = QWidget()
        position_layout = QVBoxLayout()
        position_tab.setLayout(position_layout)
        
        # Camera position and orientation combined in one group
        self._camera_pos = LinkedParameterGroup("Camera Pose")
        self._camera_pos_x = FloatParameter("X", {
            "show_label": True,
            "min": -100.0,
            "max":  100.0,
            "step": 1.0,
            "initial": 0.0
        })
        self._camera_pos_y = FloatParameter("Y", {
            "show_label": True,
            "min": -100.0,
            "max":  100.0,
            "step": 1.0,
            "initial": 0.0
        })
        self._camera_pos_z = FloatParameter("Z", {
            "show_label": True,
            "min": -100.0,
            "max":  100.0,
            "step": 1.0,
            "initial": 0.0
        })
        self._camera_pos_roll = FloatParameter("Roll", {
            "show_label": True,
            "min": -180.0,
            "max":  180.0,
            "step": 1.0,
            "initial": 0.0
        })
        self._camera_pos_pitch = FloatParameter("Pitch", {
            "show_label": True,
            "min": -180.0,
            "max":  180.0,
            "step": 1.0,
            "initial": 0.0
        })
        self._camera_pos_yaw = FloatParameter("Yaw", {
            "show_label": True,
            "min": -180.0,
            "max":  180.0,
            "step": 1.0,
            "initial": 0.0
        })
        self._camera_pos.add_parameters(
            [
                self._camera_pos_x,
                self._camera_pos_y,
                self._camera_pos_z,
                self._camera_pos_roll,
                self._camera_pos_pitch,
                self._camera_pos_yaw,
            ]
        )
        self._camera_pos.register_callback(self._on_camera_pos_changed)
        position_layout.addWidget(self._camera_pos)
        
        # Camera preset buttons
        preset_group = QGroupBox("Camera Presets")
        preset_layout = QGridLayout()
        preset_group.setLayout(preset_layout)
        
        self.front_view_btn = QPushButton("Front View")
        self.front_view_btn.clicked.connect(self._set_front_camera_view)
        preset_layout.addWidget(self.front_view_btn, 0, 0)
        
        self.top_view_btn = QPushButton("Top View")
        self.top_view_btn.clicked.connect(self._set_top_camera_view)
        preset_layout.addWidget(self.top_view_btn, 0, 1)
        
        self.follow_view_btn = QPushButton("Follow Vehicle")
        self.follow_view_btn.clicked.connect(self._set_follow_camera_view)
        preset_layout.addWidget(self.follow_view_btn, 1, 0)
        
        self.orbit_view_btn = QPushButton("Orbit View")
        self.orbit_view_btn.clicked.connect(self._set_orbit_camera_view)
        preset_layout.addWidget(self.orbit_view_btn, 1, 1)
        
        position_layout.addWidget(preset_group)
        
        # Tab 2: Focus Settings
        focus_tab = QWidget()
        focus_layout = QVBoxLayout()
        focus_tab.setLayout(focus_layout)
        
        # Manual focus toggle
        manual_focus_layout = QHBoxLayout()
        manual_focus_label = QLabel("Manual Focus:")
        manual_focus_layout.addWidget(manual_focus_label)
        
        self.manual_focus = BoolParameter("", {"initial": False})
        self.manual_focus.register_callback(self._on_manual_focus_changed)
        manual_focus_layout.addWidget(self.manual_focus)
        focus_layout.addLayout(manual_focus_layout)
        
        # Focus distance
        focus_distance_layout = QHBoxLayout()
        focus_distance_label = QLabel("Focus Distance (m):")
        focus_distance_layout.addWidget(focus_distance_label)
        
        self.focus_distance = FloatParameter("", {
            "min": 0.1,
            "max": 100.0,
            "step": 0.1,
            "initial": 1.0
        })
        self.focus_distance.register_callback(self._on_focus_distance_changed)
        focus_distance_layout.addWidget(self.focus_distance)
        focus_layout.addLayout(focus_distance_layout)
        
        # Focus aperture (f-stop)
        aperture_layout = QHBoxLayout()
        aperture_label = QLabel("Aperture (f-stop):")
        aperture_layout.addWidget(aperture_label)
        
        self.focus_aperture = FloatParameter("", {
            "min": 0.1,
            "max": 22.0,
            "step": 0.1,
            "initial": 2.8
        })
        self.focus_aperture.register_callback(self._on_focus_aperture_changed)
        aperture_layout.addWidget(self.focus_aperture)
        focus_layout.addLayout(aperture_layout)
        
        # Focus plane visualization
        focus_plane_layout = QHBoxLayout()
        focus_plane_label = QLabel("Focus Plane Visualization:")
        focus_plane_layout.addWidget(focus_plane_label)
        
        self.focus_plane = BoolParameter("", {"initial": False})
        self.focus_plane.register_callback(self._on_focus_plane_changed)
        focus_plane_layout.addWidget(self.focus_plane)
        focus_layout.addLayout(focus_plane_layout)
        
        # Tab 3: Lens Settings
        lens_tab = QWidget()
        lens_layout = QVBoxLayout()
        lens_tab.setLayout(lens_layout)
        
        # Lens presets
        lens_preset_layout = QHBoxLayout()
        lens_preset_label = QLabel("Lens Preset:")
        lens_preset_layout.addWidget(lens_preset_label)
        
        self.lens_preset = DropdownParameter("", {
            "options": ["18mm", "24mm", "35mm", "50mm", "85mm", "Custom"],
            "initial": "50mm"
        })
        self.lens_preset.register_callback(self._on_lens_preset_changed)
        lens_preset_layout.addWidget(self.lens_preset)
        lens_layout.addLayout(lens_preset_layout)
        
        # Focal length
        focal_length_layout = QHBoxLayout()
        focal_length_label = QLabel("Focal Length (mm):")
        focal_length_layout.addWidget(focal_length_label)
        
        self.focal_length = FloatParameter("", {
            "min": 12.0,
            "max": 200.0,
            "step": 1.0,
            "initial": 50.0
        })
        self.focal_length.register_callback(self._on_focal_length_changed)
        focal_length_layout.addWidget(self.focal_length)
        lens_layout.addLayout(focal_length_layout)
        
        # Tab 4: Filmback Settings
        filmback_tab = QWidget()
        filmback_layout = QVBoxLayout()
        filmback_tab.setLayout(filmback_layout)
        
        # Filmback presets
        filmback_preset_layout = QHBoxLayout()
        filmback_preset_label = QLabel("Filmback Preset:")
        filmback_preset_layout.addWidget(filmback_preset_label)
        
        self.filmback_preset = DropdownParameter("", {
            "options": ["35mm Full Frame", "35mm Academy", "Super 35mm", "APS-C", "Micro Four Thirds", "Custom"],
            "initial": "35mm Full Frame"
        })
        self.filmback_preset.register_callback(self._on_filmback_preset_changed)
        filmback_preset_layout.addWidget(self.filmback_preset)
        filmback_layout.addLayout(filmback_preset_layout)
        
        # Sensor width
        sensor_width_layout = QHBoxLayout()
        sensor_width_label = QLabel("Sensor Width (mm):")
        sensor_width_layout.addWidget(sensor_width_label)
        
        self.sensor_width = FloatParameter("", {
            "min": 5.0,
            "max": 50.0,
            "step": 0.1,
            "initial": 36.0
        })
        self.sensor_width.register_callback(self._on_filmback_size_changed)
        sensor_width_layout.addWidget(self.sensor_width)
        filmback_layout.addLayout(sensor_width_layout)
        
        # Sensor height
        sensor_height_layout = QHBoxLayout()
        sensor_height_label = QLabel("Sensor Height (mm):")
        sensor_height_layout.addWidget(sensor_height_label)
        
        self.sensor_height = FloatParameter("", {
            "min": 3.0,
            "max": 40.0,
            "step": 0.1,
            "initial": 24.0
        })
        self.sensor_height.register_callback(self._on_filmback_size_changed)
        sensor_height_layout.addWidget(self.sensor_height)
        filmback_layout.addLayout(sensor_height_layout)
        
        # Tab 5: Distortion Parameters
        distortion_tab = QWidget()
        distortion_layout = QVBoxLayout()
        distortion_tab.setLayout(distortion_layout)
        
        # K1 distortion
        k1_layout = QHBoxLayout()
        k1_label = QLabel("K1 (Barrel/Pincushion):")
        k1_layout.addWidget(k1_label)
        
        self.k1_distortion = FloatParameter("", {
            "min": -1.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.k1_distortion.register_callback(self._on_distortion_changed)
        k1_layout.addWidget(self.k1_distortion)
        distortion_layout.addLayout(k1_layout)
        
        # K2 distortion
        k2_layout = QHBoxLayout()
        k2_label = QLabel("K2:")
        k2_layout.addWidget(k2_label)
        
        self.k2_distortion = FloatParameter("", {
            "min": -1.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.k2_distortion.register_callback(self._on_distortion_changed)
        k2_layout.addWidget(self.k2_distortion)
        distortion_layout.addLayout(k2_layout)
        
        # K3 distortion
        k3_layout = QHBoxLayout()
        k3_label = QLabel("K3:")
        k3_layout.addWidget(k3_label)
        
        self.k3_distortion = FloatParameter("", {
            "min": -1.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.k3_distortion.register_callback(self._on_distortion_changed)
        k3_layout.addWidget(self.k3_distortion)
        distortion_layout.addLayout(k3_layout)
        
        # P1 distortion (tangential)
        p1_layout = QHBoxLayout()
        p1_label = QLabel("P1 (Tangential):")
        p1_layout.addWidget(p1_label)
        
        self.p1_distortion = FloatParameter("", {
            "min": -1.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.p1_distortion.register_callback(self._on_distortion_changed)
        p1_layout.addWidget(self.p1_distortion)
        distortion_layout.addLayout(p1_layout)
        
        # P2 distortion (tangential)
        p2_layout = QHBoxLayout()
        p2_label = QLabel("P2 (Tangential):")
        p2_layout.addWidget(p2_label)
        
        self.p2_distortion = FloatParameter("", {
            "min": -1.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.p2_distortion.register_callback(self._on_distortion_changed)
        p2_layout.addWidget(self.p2_distortion)
        distortion_layout.addLayout(p2_layout)
        
        # Add tabs to tab widget
        tabs.addTab(position_tab, "Position & Rotation")
        tabs.addTab(focus_tab, "Focus")
        tabs.addTab(lens_tab, "Lens")
        tabs.addTab(filmback_tab, "Filmback")
        tabs.addTab(distortion_tab, "Distortion")
        camera_layout.addWidget(tabs)
        
        # Image capture settings
        capture_group = QGroupBox("Capture Settings")
        capture_layout = QVBoxLayout()
        capture_group.setLayout(capture_layout)
        
        # Image resolution
        resolution_layout = QHBoxLayout()
        resolution_label = QLabel("Resolution:")
        resolution_layout.addWidget(resolution_label)
        
        self.cam_resolution = DropdownParameter("", {
            "options": ["640x480", "1280x720", "1920x1080", "Custom"],
            "initial": "1280x720"
        })
        self.cam_resolution.register_callback(self._on_resolution_changed)
        resolution_layout.addWidget(self.cam_resolution)
        capture_layout.addLayout(resolution_layout)
        
        # Custom resolution (only shown when "Custom" is selected)
        self.custom_resolution_layout = QHBoxLayout()
        width_label = QLabel("Width:")
        self.custom_resolution_layout.addWidget(width_label)
        
        self.custom_width = StringParameter("", {"initial": "1280"})
        self.custom_resolution_layout.addWidget(self.custom_width)
        
        height_label = QLabel("Height:")
        self.custom_resolution_layout.addWidget(height_label)
        
        self.custom_height = StringParameter("", {"initial": "720"})
        self.custom_resolution_layout.addWidget(self.custom_height)
        
        # Hide custom resolution initially
        self.custom_resolution_widget = QWidget()
        self.custom_resolution_widget.setLayout(self.custom_resolution_layout)
        self.custom_resolution_widget.setVisible(False)
        capture_layout.addWidget(self.custom_resolution_widget)
        
        # Capture buttons
        button_layout = QHBoxLayout()
        
        self.capture_btn = QPushButton("Capture Image")
        self.capture_btn.clicked.connect(self._capture_image)
        button_layout.addWidget(self.capture_btn)
        
        # Add refresh settings button
        self.refresh_settings_btn = QPushButton("Refresh Camera Settings")
        self.refresh_settings_btn.clicked.connect(self._update_camera_settings_from_current)
        button_layout.addWidget(self.refresh_settings_btn)
        
        capture_layout.addLayout(button_layout)
        camera_layout.addWidget(capture_group)
        
        # Add panel to window
        self.main_window.add_panel(camera_panel, (0, 2), row_span=3, col_span=1)
    
    #################################### TIMERS #####################################
    def _update_connection_status(self):
        """Update the connection status."""
        try:
            self.client.ping()
            if not self.is_connected:
                self.is_connected = True
                self._connect_btn.set_status("Connected", "green")
                self.logger.append("Connection established")
        except Exception as e:
            if self.is_connected:
                self.is_connected = False
                self._connect_btn.set_status("Not Connected", "red")
                self.logger.append(f"Connection lost: {e}")
            else:
                pass
    
        try:
            enabled = self.client.isApiControlEnabled(vehicle_name=self.vehicle_name.value)
            if enabled:
                self._enable_api_btn.set_status("Enabled", "green")
            else:
                self._enable_api_btn.set_status("Disabled", "red")
        except Exception as e:
            self.logger.append(f"Failed to check API control status: {e}")
            self._enable_api_btn.set_status("Disabled", "red")

    def _on_connect(self):
        """Handle the connect button click."""
        if not self.is_connected:
            try:
                self.client = airsim.MultirotorClient()
                self.client.confirmConnection()
                self.is_connected = True
                self._connect_btn.set_status("Connected", "green")
                self.logger.append("Connected to AirSim")
            except Exception as e:
                self.logger.append(f"Failed to connect to AirSim: {e}")
                self._connect_btn.set_status("Not Connected", "red")
        else:
            self.logger.append("Already connected to AirSim")
  
    def _on_enable_api(self):
        """Handle the enable API button click."""
        if not self.is_connected:
            self.logger.append("Connect to AirSim first")
            return
        
        try:
            self.client.enableApiControl(True, vehicle_name=self.vehicle_name.value)
            self._enable_api_btn.set_status("Enabled", "green")
            print("API control enabled")
        except Exception as e:
            self.logger.append(f"Failed to enable API control: {e}")
            self._enable_api_btn.set_status("Disabled", "red")

    def _on_left_joystick_moved(self, _, pos):
        """Handle left joystick movement (throttle and yaw)."""
        if not self.is_connected:
            return
            
        try:
            # Extract joystick position (normalized between -1 and 1)
            x, y = pos
            
            # Map x to yaw rate (left/right rotation) - MUCH more aggressive
            # Map y to throttle (up/down movement) - MUCH more aggressive
            yaw_rate = x * 50.0  
            throttle = y * 20.0    
            
            # Get current position and orientation
            current_state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            current_z = current_state.kinematics_estimated.position.z_val
            
            # Apply the throttle and yaw controls - using moveByAngleZAsync for continuous movement
            if abs(x) > 0.05 or abs(y) > 0.05:  # Reduced deadzone for more responsiveness
                if abs(x) > 0.05:  # Only apply yaw if joystick is moved horizontally
                    # Use rotateByYawRateAsync for continuous yaw rotation
                    self.client.rotateByYawRateAsync(
                        yaw_rate,  # Degrees per second
                        0.5,  # Shorter duration for more responsive control (was 1.0)
                        vehicle_name=self.vehicle_name.value
                    )
                
                if abs(y) > 0.05:  # Only apply throttle if joystick is moved vertically
                    # Use moveToZAsync for altitude control
                    target_z = current_z - throttle  # Subtract because AirSim Z is inverted (negative is up)
                    self.client.moveToZAsync(
                        target_z,
                        0.5,  # Doubled speed in meters per second (was 1.0)
                        vehicle_name=self.vehicle_name.value
                    )
                
                self.logger.append(f"Throttle: {round(throttle, 2)} m/s, Yaw: {round(yaw_rate, 2)} deg/s")
        except Exception as e:
            self.logger.append(f"Failed to apply throttle/yaw control: {str(e)}")
    
    def _on_right_joystick_moved(self, _, pos):
        """Handle right joystick movement (pitch and roll)."""
        if not self.is_connected:
            return
            
        try:
            # Extract joystick position (normalized between -1 and 1)
            x, y = pos
            
            # Map x to roll (left/right movement)
            # Map y to pitch (forward/backward movement)
            vx = y * 3.0     # Forward/backward velocity (y-axis of joystick)
            vy = x * 3.0    # Left/right velocity (x-axis of joystick)
            
            # Get current altitude to maintain during movement
            current_state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            current_z = current_state.kinematics_estimated.position.z_val
            
            # Apply velocity-based control while maintaining altitude
            if abs(x) > 0.05 or abs(y) > 0.05:  # Apply a small deadzone
                # Use moveByVelocityZAsync for better control
                self.client.moveByVelocityZAsync(
                    vx,              # x velocity (forward/backward)
                    vy,              # y velocity (left/right)
                    current_z,       # maintain current altitude
                    0.3,             # duration - keep moving for 1 second
                    airsim.DrivetrainType.MaxDegreeOfFreedom,  # Use forward-only drivetrain
                    # airsim.YawMode(False, 0),  # Don't control yaw
                    vehicle_name=self.vehicle_name.value
                )
                self.logger.append(f"Velocity X: {round(vx, 2)} m/s, Velocity Y: {round(vy, 2)} m/s")
        except Exception as e:
            self.logger.append(f"Failed to apply velocity control: {str(e)}")
    
    def _on_camera_pos_changed(self, _, pos):
        """Handle camera position changes from the camera panel."""
        if not self.is_connected:
            return
        
        try:
            # Extract camera position and orientation values
            x = pos["X"]
            y = pos["Y"]
            z = pos["Z"]
            roll = pos["Roll"]
            pitch = pos["Pitch"]
            yaw = pos["Yaw"]
            
            # Create camera pose
            camera_pose = airsim.Pose(
                airsim.Vector3r(x, y, z),
                airsim.Quaternionr(
                    math.radians(roll),
                    math.radians(pitch),
                    math.radians(yaw)
                )
            )
            
            # Set camera pose in AirSim
            self.client.simSetCameraPose(
                self.camera_name_widget.value,
                camera_pose,
                vehicle_name=self.vehicle_name.value
            )
            
            self.logger.append(f"Camera position set to: X={x:.1f}, Y={y:.1f}, Z={z:.1f}, Roll={roll:.1f}, Pitch={pitch:.1f}, Yaw={yaw:.1f}")
        except Exception as e:
            self.logger.append(f"Failed to set camera pose: {e}")
    
    def _set_front_camera_view(self):
        """Set camera to front view."""
        if not self.is_connected:
            return
        
        try:
            # Front view: Looking forward from behind the vehicle
            # Get the current vehicle position first
            vehicle_state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            vehicle_pos = vehicle_state.kinematics_estimated.position
            
            # Position camera behind and slightly above the vehicle
            camera_x = vehicle_pos.x_val - 5.0  # 5m behind
            camera_y = vehicle_pos.y_val        # same y-coordinate
            camera_z = vehicle_pos.z_val - 2.0  # 2m above (remember AirSim Z is inverted)
            
            # Set camera orientation to look forward
            roll = 0
            pitch = 0
            yaw = 0
            
            # Update parameter values
            self._camera_pos_x.set_value(camera_x)
            self._camera_pos_y.set_value(camera_y)
            self._camera_pos_z.set_value(camera_z)
            self._camera_pos_roll.set_value(roll)
            self._camera_pos_pitch.set_value(pitch)
            self._camera_pos_yaw.set_value(yaw)
            
            self.logger.append("Set camera to front view")
        except Exception as e:
            self.logger.append(f"Failed to set front view: {e}")
    
    def _set_top_camera_view(self):
        """Set camera to top-down view."""
        if not self.is_connected:
            return
        
        try:
            # Top view: Looking down at the vehicle from above
            # Get the current vehicle position
            vehicle_state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            vehicle_pos = vehicle_state.kinematics_estimated.position
            
            # Position camera directly above the vehicle
            camera_x = vehicle_pos.x_val
            camera_y = vehicle_pos.y_val
            camera_z = vehicle_pos.z_val - 20.0  # 20m above (AirSim Z is inverted)
            
            # Set camera to look straight down
            roll = 0
            pitch = 90  # Looking straight down
            yaw = 0
            
            # Update parameter values
            self._camera_pos_x.set_value(camera_x)
            self._camera_pos_y.set_value(camera_y)
            self._camera_pos_z.set_value(camera_z)
            self._camera_pos_roll.set_value(roll)
            self._camera_pos_pitch.set_value(pitch)
            self._camera_pos_yaw.set_value(yaw)
            
            self.logger.append("Set camera to top-down view")
        except Exception as e:
            self.logger.append(f"Failed to set top view: {e}")
    
    def _set_follow_camera_view(self):
        """Set camera to follow the vehicle."""
        if not self.is_connected:
            return
        
        try:
            # Follow view: Position behind and slightly above the vehicle
            # Get the current vehicle position and orientation
            vehicle_state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            vehicle_pos = vehicle_state.kinematics_estimated.position
            vehicle_orientation = vehicle_state.kinematics_estimated.orientation
            
            # Get vehicle yaw to determine its forward direction
            _, _, vehicle_yaw = airsim.to_eularian_angles(vehicle_orientation)
            vehicle_yaw_deg = math.degrees(vehicle_yaw)
            
            # Calculate position behind the vehicle based on its orientation
            distance_behind = 5.0  # 5m behind
            height_above = 2.0     # 2m above
            
            # Calculate offset based on vehicle orientation
            offset_x = -distance_behind * math.cos(vehicle_yaw)
            offset_y = -distance_behind * math.sin(vehicle_yaw)
            
            camera_x = vehicle_pos.x_val + offset_x
            camera_y = vehicle_pos.y_val + offset_y
            camera_z = vehicle_pos.z_val - height_above  # Subtract because AirSim Z is inverted
            
            # Set camera to look at the vehicle
            roll = 0
            pitch = -15  # Slight downward angle
            yaw = vehicle_yaw_deg  # Match vehicle yaw
            
            # Update parameter values
            self._camera_pos_x.set_value(camera_x)
            self._camera_pos_y.set_value(camera_y)
            self._camera_pos_z.set_value(camera_z)
            self._camera_pos_roll.set_value(roll)
            self._camera_pos_pitch.set_value(pitch)
            self._camera_pos_yaw.set_value(yaw)
            
            self.logger.append("Set camera to follow vehicle view")
        except Exception as e:
            self.logger.append(f"Failed to set follow view: {e}")
    
    def _set_orbit_camera_view(self):
        """Set camera to orbit around the vehicle."""
        if not self.is_connected:
            return
        
        try:
            # Orbit view: Position at an angle to the vehicle
            # Get the current vehicle position
            vehicle_state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            vehicle_pos = vehicle_state.kinematics_estimated.position
            
            # Calculate orbit position (45 degrees to the side and above)
            orbit_distance = 8.0  # 8m away
            orbit_height = 3.0    # 3m above
            orbit_angle = math.radians(45)  # 45 degree angle
            
            camera_x = vehicle_pos.x_val + orbit_distance * math.cos(orbit_angle)
            camera_y = vehicle_pos.y_val + orbit_distance * math.sin(orbit_angle)
            camera_z = vehicle_pos.z_val - orbit_height  # Subtract because AirSim Z is inverted
            
            # Calculate camera orientation to look at the vehicle
            dx = vehicle_pos.x_val - camera_x
            dy = vehicle_pos.y_val - camera_y
            dz = vehicle_pos.z_val - camera_z
            
            # Calculate yaw angle (in degrees)
            yaw = math.degrees(math.atan2(dy, dx))
            
            # Calculate pitch angle (in degrees)
            horizontal_distance = math.sqrt(dx*dx + dy*dy)
            pitch = math.degrees(math.atan2(dz, horizontal_distance))
            
            # Set camera orientation
            roll = 0
            
            # Update parameter values
            self._camera_pos_x.set_value(camera_x)
            self._camera_pos_y.set_value(camera_y)
            self._camera_pos_z.set_value(camera_z)
            self._camera_pos_roll.set_value(roll)
            self._camera_pos_pitch.set_value(pitch)
            self._camera_pos_yaw.set_value(yaw)
            
            self.logger.append("Set camera to orbit view")
        except Exception as e:
            self.logger.append(f"Failed to set orbit view: {e}")
    
    def _sync_with_camera_panel(self):
        """Synchronize camera position between parameters panel and camera panel."""
        if not self.is_connected:
            return
        
        try:
            # Get current camera position from the camera panel
            camera_info = self.client.simGetCameraInfo(
                self.camera_name_widget.value,
                vehicle_name=self.vehicle_name.value
            )
            
            if camera_info:
                # Get position
                x = camera_info.pose.position.x_val
                y = camera_info.pose.position.y_val
                z = camera_info.pose.position.z_val
                
                # Get orientation and convert to Euler angles
                q = camera_info.pose.orientation
                roll_rad, pitch_rad, yaw_rad = airsim.to_eularian_angles(q)
                
                # Convert to degrees
                roll = math.degrees(roll_rad)
                pitch = math.degrees(pitch_rad)
                yaw = math.degrees(yaw_rad)
                
                # Update parameter panel controls
                self._camera_pos_x.set_value(x, trigger_callback=False)
                self._camera_pos_y.set_value(y, trigger_callback=False)
                self._camera_pos_z.set_value(z, trigger_callback=False)
                self._camera_pos_roll.set_value(roll, trigger_callback=False)
                self._camera_pos_pitch.set_value(pitch, trigger_callback=False)
                self._camera_pos_yaw.set_value(yaw, trigger_callback=False)
                
                self.logger.append("Synchronized camera position from camera panel")
            else:
                self.logger.append("Failed to get camera info")
        except Exception as e:
            self.logger.append(f"Failed to synchronize camera position: {e}")
    
    #################################### CALLBACKS #####################################
    def _on_camera_type_changed(self):
        """Handle camera type change."""
        if not self.is_connected:
            return
        
        try:
            camera_type_map = {
                "Scene": airsim.ImageType.Scene,
                "Depth": airsim.ImageType.DepthVis,
                "Segmentation": airsim.ImageType.Segmentation,
                "Normals": airsim.ImageType.SurfaceNormals
            }
            
            camera_type = camera_type_map.get(self.cam_type.value, airsim.ImageType.Scene)
            self.logger.append(f"Camera type set to: {self.cam_type.value}")
        except Exception as e:
            self.logger.append(f"Failed to set camera type: {e}")
    
    def _on_camera_fov_changed(self):
        """Handle camera FOV change."""
        if not self.is_connected:
            return
        
        try:
            fov = self.cam_fov.value
            self.client.simSetCameraFov(self.camera_name_widget.value, fov, vehicle_name=self.vehicle_name.value)
            self.logger.append(f"Camera FOV set to: {fov} degrees")
        except Exception as e:
            self.logger.append(f"Failed to set camera FOV: {e}")
    
    def _on_camera_position_changed(self):
        """Handle camera position change."""
        if not self.is_connected:
            return
        
        try:
            x = self.cam_pos_x.value
            y = self.cam_pos_y.value
            z = self.cam_pos_z.value
            
            camera_pose = airsim.Pose(airsim.Vector3r(x, y, z))
            self.client.simSetCameraPose(self.camera_name_widget.value, camera_pose, vehicle_name=self.vehicle_name.value)
            self.logger.append(f"Camera position set to: X={x}, Y={y}, Z={z}")
        except Exception as e:
            self.logger.append(f"Failed to set camera position: {e}")
    
    def _on_camera_rotation_changed(self):
        """Handle camera rotation change."""
        if not self.is_connected:
            return
        
        try:
            roll = self.cam_roll.value
            pitch = self.cam_pitch.value
            yaw = self.cam_yaw.value
            
            # Convert degrees to quaternion
            q = airsim.to_quaternion(math.radians(roll), math.radians(pitch), math.radians(yaw))
            camera_pose = self.client.simGetCameraPose(self.camera_name_widget.value, vehicle_name=self.vehicle_name.value)
            camera_pose.orientation = q
            
            self.client.simSetCameraPose(self.camera_name_widget.value, camera_pose, vehicle_name=self.vehicle_name.value)
            self.logger.append(f"Camera rotation set to: Roll={roll}, Pitch={pitch}, Yaw={yaw}")
        except Exception as e:
            self.logger.append(f"Failed to set camera rotation: {e}")
    
    def _capture_image(self):
        """Capture an image from the camera."""
        if not self.is_connected:
            self.logger.append("Connect to AirSim first to capture an image")
            return
        
        try:
            # Get the camera type from the dropdown
            camera_type_map = {
                "Scene": airsim.ImageType.Scene,
                "Depth": airsim.ImageType.DepthVis,
                "Segmentation": airsim.ImageType.Segmentation,
                "Normals": airsim.ImageType.SurfaceNormals
            }
            
            camera_type = camera_type_map.get(self.cam_type.value, airsim.ImageType.Scene)
            
            # Capture the image
            response = self.client.simGetImage(
                self.camera_name_widget.value,
                camera_type,
                vehicle_name=self.vehicle_name.value
            )
            
            if response:
                # Create a timestamp for the filename
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                filename = f"airsim_{self.cam_type.value.lower()}_{timestamp}.png"
                
                # Save the image to file
                with open(filename, 'wb') as f:
                    f.write(response)
                
                self.logger.append(f"Image captured and saved as '{filename}'")
            else:
                self.logger.append("Failed to capture image: No response from camera")
        except Exception as e:
            self.logger.append(f"Failed to capture image: {e}")
    
    def _toggle_recording(self):
        """Toggle image recording."""
        if not self.is_connected:
            return
        
        try:
            if self.recording:
                self.client.simStopRecording()
                self.recording = False
                self.record_btn.setText("Start Recording")
                self.logger.append("Image recording stopped")
            else:
                self.client.simStartRecording()
                self.recording = True
                self.record_btn.setText("Stop Recording")
                self.logger.append("Image recording started")
        except Exception as e:
            self.logger.append(f"Failed to toggle recording: {e}")
    
    def _setup_vehicle_control_panel(self):
        """Set up the vehicle control panel."""
        # Create a parameter panel for vehicle controls
        vehicle_panel = ParameterGroup("Vehicle Controls")
        
        # Create a parameter group for movement
        movement_group = ParameterGroup("Movement")
        
        # Add joystick for xy movement
        self.vehicle_joystick = JoystickParameter("Move", {"initial": (0.0, 0.0)})
        self.vehicle_joystick.register_callback(self._update_vehicle_movement)
        
        # Add altitude slider
        self.altitude = FloatParameter("Altitude", {"min": -10.0, "max": 100.0, "step": 1.0, "initial": 0.0})
        self.altitude.register_callback(self._update_vehicle_altitude)
        
        # Add yaw slider
        self.vehicle_yaw = FloatParameter("Yaw", {"min": -180.0, "max": 180.0, "step": 1.0, "initial": 0.0})
        self.vehicle_yaw.register_callback(self._update_vehicle_yaw)
        
        # Add parameters to group
        movement_group.add_parameters([self.vehicle_joystick, self.altitude, self.vehicle_yaw])
        
        # Create a parameter group for actions
        action_group = ParameterGroup("Actions")
        
        # Add action buttons
        self.takeoff_btn = ActionParameter("Takeoff")
        self.takeoff_btn.register_callback(self._takeoff)
        self.land_btn = ActionParameter("Land")
        self.land_btn.register_callback(self._land)
        self.hover_btn = ActionParameter("Hover")
        self.hover_btn.register_callback(self._reset)
        self.reset_btn = ActionParameter("Reset")
        self.reset_btn.register_callback(self._reset)
        
        # Add parameters to group
        action_group.add_parameters([self.takeoff_btn, self.land_btn, self.hover_btn, self.reset_btn])
        
        # Add groups to main group
        vehicle_panel.add_parameters([movement_group, action_group])
        
        # Add panel to window at position (0, 0)
        self.window.add_panel(vehicle_panel, (0, 0), "Vehicle Controls")
    
    def _setup_environment_panel(self):
        """Set up the environment control panel."""
        # Create a parameter panel for environment controls
        env_panel = ParameterGroup("Environment")
        
        # Create a parameter group for weather
        weather_group = ParameterGroup("Weather")
        
        # Add weather sliders
        self.rain = FloatParameter("Rain", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0})
        self.snow = FloatParameter("Snow", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0})
        self.leaf = FloatParameter("Leaf", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0})
        self.dust = FloatParameter("Dust", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0})
        self.fog = FloatParameter("Fog", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0})
        
        # Connect weather sliders to update function
        self.rain.register_callback(self._update_weather)
        self.snow.register_callback(self._update_weather)
        self.leaf.register_callback(self._update_weather)
        self.dust.register_callback(self._update_weather)
        self.fog.register_callback(self._update_weather)
        
        # Add parameters to group
        weather_group.add_parameters([self.rain, self.snow, self.leaf, self.dust, self.fog])
        
        # Create a parameter group for time
        time_group = ParameterGroup("Time")
        
        # Add time sliders
        self.time_of_day = FloatParameter("Time of Day", {"min": 0.0, "max": 24.0, "step": 0.1, "initial": 12.0})
        self.time_of_day.register_callback(self._update_time_of_day)
        
        # Add parameters to group
        time_group.add_parameters([self.time_of_day])
        
        # Create a parameter group for physics
        physics_group = ParameterGroup("Physics")
        
        # Add physics toggle
        self.enable_physics = BoolParameter("Enable Physics", {"initial": True})
        self.enable_physics.register_callback(self._update_physics)
        
        # Add parameters to group
        physics_group.add_parameters([self.enable_physics])
        
        # Add groups to panel
        env_panel.add_parameters([weather_group, time_group, physics_group])
        
        # Add panel to window at position (0, 1)
        self.window.add_panel(env_panel, (0, 1), "Environment")
    
    def _setup_camera_view_panel(self):
        pass
    
    def _update_camera_fov(self):
        """Update the camera FOV."""
        if not self.is_connected:
            return
        
        try:
            self.client.simSetFocusAperture(self.cam_fov.value)
        except Exception as e:
            print(f"Failed to update camera FOV: {e}")
    
    def _update_camera_type(self):
        """Update the camera type."""
        self.current_camera_type = self.cam_type.value
    
    def _update_vehicle_movement(self):
        """Update the vehicle movement."""
        if not self.is_connected:
            return
        
        try:
            # Get joystick values
            vx, vy = self.vehicle_joystick.value 
            
            # Set vehicle movement
            self.client.moveByVelocityBodyFrameAsync(vx, vy, 0, 0.1)
        except Exception as e:
            print(f"Failed to update vehicle movement: {e}")
    
    def _update_vehicle_altitude(self):
        """Update the vehicle altitude."""
        if not self.is_connected:
            return
        
        try:
            # Set vehicle altitude
            self.client.moveToZAsync(self.altitude.value, 1.0)
        except Exception as e:
            print(f"Failed to update vehicle altitude: {e}")
    
    def _update_vehicle_yaw(self):
        """Update the vehicle yaw."""
        if not self.is_connected:
            return
        
        try:
            # Set vehicle yaw
            self.client.rotateToYawAsync(self.vehicle_yaw.value, 1.0)
        except Exception as e:
            print(f"Failed to update vehicle yaw: {e}")
    
    def _takeoff(self):
        """Takeoff the vehicle."""
        if not self.is_connected:
            return
        
        try:
            self.client.takeoffAsync()
            self.logger.append("Taking off...")
        except Exception as e:
            print(f"Failed to take off: {e}")
    
    def _land(self):
        """Land the vehicle."""
        if not self.is_connected:
            return
        
        try:
            self.client.landAsync()
            print("Landing...")
        except Exception as e:
            print(f"Failed to land: {e}")
            
    def _arm(self):
        """Disarm the vehicle."""
        if not self.is_connected:
            return
        
        try:
            self.client.armDisarm(True)
            self.logger.append("Arming...")
        except Exception as e:
            self.logger.append(f"Failed to arm: {e}")   
    
    def _return_to_launch(self):
        """Return the vehicle to launch (RTL)."""
        if not self.is_connected:
            return
        
        try:
            self.client.goHomeAsync()
            self.logger.append("Returning to launch...")
        except Exception as e:
            self.logger.append(f"Failed to return to launch: {e}")
    
    def _reset(self):
        """Reset the simulation."""
        if not self.is_connected:
            return
        
        try:
            self.client.reset()
            print("Simulation reset.")
        except Exception as e:
            print(f"Failed to reset simulation: {e}")
    
    def _update_weather(self):
        """Update the weather."""
        if not self.is_connected:
            return
        
        try:
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Rain, self.rain.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Snow, self.snow.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Leaf, self.leaf.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Dust, self.dust.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Fog, self.fog.value)
        except Exception as e:
            print(f"Failed to update weather: {e}")
    
    def _update_time_of_day(self):
        """Update the time of day."""
        if not self.is_connected:
            return
        
        try:
            # Assuming there's a method for setting time of day
            # This might vary based on the specific AirSim version and implementation
            # self.client.simSetTimeOfDay(self.time_of_day.value)
            pass
        except Exception as e:
            print(f"Failed to update time of day: {e}")
    

    def _update_camera_view(self):
        """Update the camera view."""
        if not self.is_connected:
            return
        
        try:
            # Get image based on selected camera type
            camera_type = self.cam_type.value
            
            if camera_type == "Depth":
                responses = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthVis, False, False)])
            elif camera_type == "Segmentation":
                responses = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Segmentation, False, False)])
            elif camera_type == "Normals":
                responses = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.SurfaceNormals, False, False)])
            else:  # Scene
                responses = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
            
            if responses:
                img1d = np.fromstring(responses[0].image_data_uint8, dtype=np.uint8)
                img_rgba = img1d.reshape(responses[0].height, responses[0].width, 4)
                img_rgba = np.flipud(img_rgba)  # Flip image vertically
                
                # Convert to QImage and display
                img = QImage(img_rgba.data, img_rgba.shape[1], img_rgba.shape[0], QImage.Format_RGBA8888)
                pixmap = QPixmap.fromImage(img)
                self.camera_view_label.setPixmap(pixmap.scaled(self.camera_view_label.width(), 
                                                             self.camera_view_label.height(), 
                                                             Qt.KeepAspectRatio))
        except Exception as e:
            print(f"Failed to update camera view: {e}")
    
    def run(self):
        """Run the application."""
        self.app.run()

    def _debug_callback(self, *args, **kwargs):
        """Main callback function."""
        self.logger.append("Main callback executed.")
        self.logger.append(f"Arguments: {args}, Keyword Arguments: {kwargs}")
        self.logger.append("--------------------------------------------------")

        pass

    def _on_resolution_changed(self):
        """Handle resolution change for image capture."""
        if self.cam_resolution.value == "Custom":
            self.custom_resolution_widget.setVisible(True)
        else:
            self.custom_resolution_widget.setVisible(False)
    
    def _on_manual_focus_changed(self):
        """Handle manual focus toggle."""
        if not self.is_connected:
            return
        
        try:
            enable_manual = self.manual_focus.value
            self.client.simEnableManualFocus(
                enable_manual, 
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            status = "enabled" if enable_manual else "disabled"
            self.logger.append(f"Manual focus {status}")
        except Exception as e:
            self.logger.append(f"Failed to set manual focus: {e}")
    
    def _on_focus_distance_changed(self):
        """Handle focus distance change."""
        if not self.is_connected:
            return
        
        try:
            distance = self.focus_distance.value
            self.client.simSetFocusDistance(
                distance, 
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            self.logger.append(f"Focus distance set to: {distance} meters")
        except Exception as e:
            self.logger.append(f"Failed to set focus distance: {e}")
    
    def _on_focus_aperture_changed(self):
        """Handle focus aperture (f-stop) change."""
        if not self.is_connected:
            return
        
        try:
            aperture = self.focus_aperture.value
            self.client.simSetFocusAperture(
                aperture, 
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            self.logger.append(f"Focus aperture set to: f/{aperture}")
        except Exception as e:
            self.logger.append(f"Failed to set focus aperture: {e}")
    
    def _on_focus_plane_changed(self):
        """Handle focus plane visualization toggle."""
        if not self.is_connected:
            return
        
        try:
            enable_plane = self.focus_plane.value
            self.client.simEnableFocusPlane(
                enable_plane, 
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            status = "enabled" if enable_plane else "disabled"
            self.logger.append(f"Focus plane visualization {status}")
        except Exception as e:
            self.logger.append(f"Failed to toggle focus plane: {e}")
    
    def _on_lens_preset_changed(self):
        """Handle lens preset selection."""
        if not self.is_connected:
            return
        
        try:
            preset = self.lens_preset.value
            
            # Only apply preset if not "Custom"
            if preset != "Custom":
                # Update focal length based on preset
                # Extract numeric value from preset (e.g. "50mm" -> 50.0)
                focal_length = float(preset.replace("mm", ""))
                
                # Update the focal length widget value
                self.focal_length.set_value(focal_length)
                
                # Apply the focal length to the camera
                self.client.simSetFocalLength(
                    focal_length, 
                    self.camera_name_widget.value, 
                    vehicle_name=self.vehicle_name.value
                )
                
                self.logger.append(f"Applied lens preset: {preset} (focal length: {focal_length}mm)")
            
            # Get current preset lens settings
            current_presets = self.client.simGetPresetLensSettings(
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            if current_presets:
                self.logger.append(f"Available lens presets: {current_presets}")
            
        except Exception as e:
            self.logger.append(f"Failed to set lens preset: {e}")
    
    def _on_focal_length_changed(self):
        """Handle focal length change."""
        if not self.is_connected:
            return
        
        try:
            focal_length = self.focal_length.value
            self.client.simSetFocalLength(
                focal_length, 
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            
            # Set lens preset to "Custom" when manually changing focal length
            if self.lens_preset.value != "Custom":
                self.lens_preset.setCurrentIndex(self.lens_preset.findText("Custom"))
            
            self.logger.append(f"Focal length set to: {focal_length}mm")
            
            # Get current field of view based on the new focal length
            try:
                current_fov = self.client.simGetCurrentFieldOfView(
                    self.camera_name_widget.value, 
                    vehicle_name=self.vehicle_name.value
                )
                if current_fov:
                    self.logger.append(f"Current field of view: {current_fov} degrees")
            except Exception:
                # Field of view calculation might not be available
                pass
            
        except Exception as e:
            self.logger.append(f"Failed to set focal length: {e}")
    
    def _on_filmback_preset_changed(self):
        """Handle filmback preset selection."""
        if not self.is_connected:
            return
        
        try:
            preset = self.filmback_preset.value
            
            # Define standard sensor sizes for common filmback formats
            preset_sizes = {
                "35mm Full Frame": (36.0, 24.0),
                "35mm Academy": (22.0, 16.0),
                "Super 35mm": (24.89, 18.66),
                "APS-C": (23.6, 15.6),
                "Micro Four Thirds": (17.3, 13.0),
            }
            
            # Only apply preset if not "Custom"
            if preset != "Custom" and preset in preset_sizes:
                width, height = preset_sizes[preset]
                
                # Update the sensor size widgets
                self.sensor_width.set_value(width)
                self.sensor_height.set_value(height)
                
                # Apply the filmback settings to the camera
                self.client.simSetFilmbackSettings(
                    width, 
                    height, 
                    self.camera_name_widget.value, 
                    vehicle_name=self.vehicle_name.value
                )
                
                self.logger.append(f"Applied filmback preset: {preset} ({width}mm x {height}mm)")
            
            # Get current preset filmback settings
            current_presets = self.client.simGetPresetFilmbackSettings(
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            if current_presets:
                self.logger.append(f"Available filmback presets: {current_presets}")
            
        except Exception as e:
            self.logger.append(f"Failed to set filmback preset: {e}")
    
    def _on_filmback_size_changed(self):
        """Handle filmback size (sensor width/height) change."""
        if not self.is_connected:
            return
        
        try:
            width = self.sensor_width.value
            height = self.sensor_height.value
            
            success = self.client.simSetFilmbackSettings(
                width, 
                height, 
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            
            if success:
                # Set filmback preset to "Custom" when manually changing sensor size
                if self.filmback_preset.value != "Custom":
                    self.filmback_preset.setCurrentIndex(self.filmback_preset.findText("Custom"))
                
                self.logger.append(f"Filmback size set to: {width}mm x {height}mm")
                
                # Get current filmback settings to confirm changes
                current_settings = self.client.simGetFilmbackSettings(
                    self.camera_name_widget.value, 
                    vehicle_name=self.vehicle_name.value
                )
                if current_settings:
                    self.logger.append(f"Current filmback settings: {current_settings}")
            else:
                self.logger.append("Failed to set filmback settings: No success response")
            
        except Exception as e:
            self.logger.append(f"Failed to set filmback size: {e}")
    
    def _on_distortion_changed(self):
        """Handle lens distortion parameter changes."""
        if not self.is_connected:
            return
        
        try:
            # Create distortion parameters dictionary
            distortion_params = {
                "K1": self.k1_distortion.value,
                "K2": self.k2_distortion.value,
                "K3": self.k3_distortion.value,
                "P1": self.p1_distortion.value,
                "P2": self.p2_distortion.value
            }
            
            # Apply all distortion parameters at once
            self.client.simSetDistortionParams(
                self.camera_name_widget.value,
                distortion_params,
                vehicle_name=self.vehicle_name.value
            )
            
            self.logger.append(f"Applied camera distortion parameters: {distortion_params}")
            
            # Get current distortion parameters to confirm changes
            current_params = self.client.simGetDistortionParams(
                self.camera_name_widget.value, 
                vehicle_name=self.vehicle_name.value
            )
            if current_params:
                self.logger.append(f"Current distortion parameters: {current_params}")
            
        except Exception as e:
            self.logger.append(f"Failed to set distortion parameters: {e}")
    
    def _update_camera_settings_from_current(self):
        """Update all camera setting controls from current camera settings."""
        if not self.is_connected:
            return
        
        try:
            camera_name = self.camera_name_widget.value
            vehicle_name = self.vehicle_name.value
            
            # Get camera info
            try:
                camera_info = self.client.simGetCameraInfo(camera_name, vehicle_name)
                if camera_info:
                    # Update position and rotation controls
                    self.cam_pos_x.set_value(camera_info.pose.position.x_val)
                    self.cam_pos_y.setValue(camera_info.pose.position.y_val)
                    self.cam_pos_z.setValue(camera_info.pose.position.z_val)
                    
                    # Convert quaternion to Euler angles
                    q = camera_info.pose.orientation
                    roll, pitch, yaw = airsim.to_eularian_angles(q)
                    
                    self.cam_roll.setValue(math.degrees(roll))
                    self.cam_pitch.setValue(math.degrees(pitch))
                    self.cam_yaw.setValue(math.degrees(yaw))
                    
                    # Update FOV
                    self.cam_fov.setValue(camera_info.fov)
            except Exception as e:
                self.logger.append(f"Could not get camera info: {e}")
            
            # Get focal length
            try:
                focal_length = self.client.simGetFocalLength(camera_name, vehicle_name)
                if focal_length:
                    self.focal_length.setValue(focal_length)
            except Exception as e:
                self.logger.append(f"Could not get focal length: {e}")
            
            # Get focus distance
            try:
                focus_distance = self.client.simGetFocusDistance(camera_name, vehicle_name)
                if focus_distance:
                    self.focus_distance.setValue(focus_distance)
            except Exception as e:
                self.logger.append(f"Could not get focus distance: {e}")
            
            # Get focus aperture
            try:
                focus_aperture = self.client.simGetFocusAperture(camera_name, vehicle_name)
                if focus_aperture:
                    self.focus_aperture.setValue(focus_aperture)
            except Exception as e:
                self.logger.append(f"Could not get focus aperture: {e}")
            
            # Get filmback settings
            try:
                filmback_settings = self.client.simGetFilmbackSettings(camera_name, vehicle_name)
                if filmback_settings and isinstance(filmback_settings, str):
                    self.logger.append(f"Current filmback settings: {filmback_settings}")
                # This would need parsing of the returned settings to update the UI
            except Exception as e:
                self.logger.append(f"Could not get filmback settings: {e}")
            
            # Get distortion parameters
            try:
                distortion_params = self.client.simGetDistortionParams(camera_name, vehicle_name)
                if distortion_params and len(distortion_params) >= 5:
                    # Assuming the order is K1, K2, K3, P1, P2
                    self.k1_distortion.setValue(distortion_params[0])
                    self.k2_distortion.setValue(distortion_params[1])
                    self.k3_distortion.setValue(distortion_params[2])
                    self.p1_distortion.setValue(distortion_params[3])
                    self.p2_distortion.setValue(distortion_params[4])
            except Exception as e:
                self.logger.append(f"Could not get distortion parameters: {e}")
            
            self.logger.append("Updated camera settings from current configuration")
        except Exception as e:
            self.logger.append(f"Failed to update camera settings from current: {e}")

    def _toggle_hover(self):
        """Toggle hover mode for the vehicle."""
        if not self.is_connected:
            self.logger.append("Connect to AirSim first")
            return
        
        try:
            # Get current state of the vehicle
            current_state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            
            if not self.hover_active:
                # Enable hover mode by setting zero velocity at current position and altitude
                current_pos = current_state.kinematics_estimated.position
                current_z = current_pos.z_val
                current_yaw = airsim.to_eularian_angles(current_state.kinematics_estimated.orientation)[2]
                
                # Call hover API to maintain position
                self.client.hoverAsync(vehicle_name=self.vehicle_name.value)
                
                # Update button text and state
                self._hover_btn.setText("Cancel Hover")
                self.hover_active = True
                self.logger.append("Hover mode activated - maintaining current position")
            else:
                # Disable hover mode
                # No specific API call needed - just update the state
                self._hover_btn.setText("Hover")
                self.hover_active = False
                self.logger.append("Hover mode deactivated")
                
        except Exception as e:
            self.logger.append(f"Failed to toggle hover mode: {e}")
            self._hover_btn.setText("Hover")
            self.hover_active = False

if __name__ == "__main__":
    app = AirSimGUI()
    app.run()