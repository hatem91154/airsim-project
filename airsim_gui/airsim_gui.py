#!/usr/bin/env python3
"""
AirSim GUI - Main Application
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
    QTabWidget,
    QScrollArea
)

# import spacer QSpacerItem and QSizePolicy
from PyQt5.QtWidgets import QSpacerItem, QSizePolicy

# import pysignal
from PyQt5.QtCore import pyqtSignal, QObject

import cosysairsim as airsim


# Import from pyqt_live_tuner library
from pyqt_live_tuner.app import LiveTunerApp
from pyqt_live_tuner.main_window import MainWindow
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

# Additional imports for multi-camera display
from pyqt_live_tuner.displays.image import ImageDisplay


class ButtonWithStatus(QWidget):
    """Button with status label."""

    clicked = pyqtSignal()

    def __init__(self, text):
        """Initialize the button with a status label."""
        super().__init__()
        
        layout = QHBoxLayout()
        margin = 0
        layout.setContentsMargins(margin, margin, margin, margin)  # Minimal margins
        # layout.setSpacing(2)  # Minimal spacing
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

from PyQt5.QtCore import QObject, QEvent, Qt

class AirSimEventFilter(QObject):
    def __init__(self, gui_instance):
        super().__init__()
        self.gui_instance = gui_instance

    def eventFilter(self, obj, event):
        """Forward event to AirSimGUI's handler."""
        return self.gui_instance._handle_event(obj, event)


class AirSimGUI:
    """AirSim GUI using pyqt_live_tuner library."""

    def __init__(self):
        """Initialize the AirSim GUI."""
        # Create the LiveTunerApp
        self.app = LiveTunerApp("AirSim GUI", True)
        
        # Create the main window
        self.main_window = self.app.main_window
        
        # Initialize AirSim client if available
        self.client = airsim.MultirotorClient()
        self.vehicle_name = "SimpleFlight"
        self.camera_name = "0"
        self.is_connected = False
        self.recording = False  # Track recording state
        self.hover_active = False  # Track hover mode state
        
        # Import AirSim settings editor
        from airsim_settings_editor import AirSimSettingsEditor
        self.settings_editor = None
        
        # Create a scrollable area for all system parameters
        self.system_parameters_scroll_area = QScrollArea()
        self.system_parameters_scroll_area.setWidgetResizable(True)
        self.system_parameters_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.system_parameters_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create a widget to hold all parameter groups with horizontal layout
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()  # Using horizontal layout
        # self.scroll_layout.setSpacing(10)
        self.scroll_content.setLayout(self.scroll_layout)
        self.system_parameters_scroll_area.setWidget(self.scroll_content)
        
        # Set up the GUI
        self._setup_configuration_panel()
        self._setup_action_panel()  # Re-enable action panel setup
        self._setup_camera_panel()  # Enable camera panel with integrated camera position controls
        self._setup_weather_panel() # Set up weather panel with wind controls
        # self._setup_environment_panel()

        # create Logger 
        logger_panel = QGroupBox("Log")
        logger_panel.setMaximumWidth(330)
        # logger_panel.setMaximumHeight(200)
        # logger_panel.setMinimumHeight(200)
        
        logger_layout = QVBoxLayout()
        
        self.logger = QTextEdit()
        # decrease font size
        font = self.logger.font()
        font.setPointSize(8)
        self.logger.setFont(font)
        
        self._logger_clearn_btn = QPushButton("Clear")
        self._logger_clearn_btn.clicked.connect(self.logger.clear)
        

        logger_layout.addWidget(self.logger)
        logger_layout.addWidget(self._logger_clearn_btn)

        logger_panel.setLayout(logger_layout)

        # Add panel to window
        self.main_window.add_panel(logger_panel, (2, 0), row_span=2, col_span=1)


        # Create a timer for updating the connection status
        self._connection_timer = QTimer()
        self._connection_timer.timeout.connect(self._update_connection_status)
        self._connection_timer.start(1000)

        # Set up a simple drone status panel
        self._setup_drone_status_panel()

        # Set up the image display panel for multi-camera viewing
        self._setup_image_display()

        self._event_filter = AirSimEventFilter(self)
        self.main_window.installEventFilter(self._event_filter)
        self._keyboard_pressed = False


    def _handle_event(self, obj, event):
        """Original eventFilter logic moved here."""
        if event.type() == event.KeyPress and obj is self.main_window:
            
            throttle_value, yaw_value = 0.2, math.radians(60)  # Default values for throttle and yaw
            throttle, yaw = 0, 0
            
            try:
                if event.key() == Qt.Key_A:
                    yaw = -yaw_value  # Rotate left
                if event.key() == Qt.Key_D:
                    yaw = yaw_value
                if event.key() == Qt.Key_W:
                    throttle = throttle_value
                if event.key() == Qt.Key_S:
                    throttle = -throttle_value
                
                self._handle_throttle_yaw_keyboard_event(throttle, yaw)

            except Exception as e:
                self.logger.append(f"Keyboard control error: {str(e)}")
            return True
        return False
    
    def _handle_throttle_yaw_keyboard_event(self, throttle, yaw):
        """Handle throttle and yaw events from keyboard."""
        if not self.is_connected:
            self.logger.append("Not connected to AirSim")
            return
        self._keyboard_pressed = True
        self._right_joystick.blockSignals(True)
        
        try:
            vx, vy = self._right_joystick.value
            vx = math.radians(vx * 10.0)  # Scale for forward/backward movement
            vy = math.radians(vy * 10.0)  # Scale for left/right movement

            current_z = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value).kinematics_estimated.position.z_val

            # Apply the throttle and yaw controls
            self.client.moveByRollPitchYawrateZAsync(
                roll=vx,
                pitch=vy,
                yaw_rate=-yaw,
                z=current_z,
                duration=0.1,
            )
            self.logger.append(f"Throttle: {round(throttle, 2)} m/s, Yaw: {round(yaw, 2)} deg/s")
        except Exception as e:
            self.logger.append(f"Failed to apply throttle/yaw control: {str(e)}")
        
        self._right_joystick.blockSignals(False)
        self._keyboard_pressed = False

    def _setup_configuration_panel(self):
        """Set up the configuration panel."""
        # Create a parameter panel for configuration
        config_panel = QGroupBox("Configuration")
        config_panel.setMaximumHeight(170)
        config_panel.setMaximumWidth(330)
        config_layout = QVBoxLayout()
        # config_layout.setContentsMargins(0, 0, 0, 0)
        # config_layout.setSpacing(2)

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
        
        # Add button to open AirSim settings editor
        self.open_settings_editor_btn = QPushButton("AirSim Settings Editor")
        self.open_settings_editor_btn.clicked.connect(self._open_airsim_settings_editor)
        config_layout.addWidget(self.open_settings_editor_btn)
               
        # Add panel to window at position (0, 0)
        self.main_window.add_panel(config_panel, (0, 0))
    
    def _setup_action_panel(self):
        """Set up the action panel."""
        action_panel = QGroupBox("Control")

        action_layout = QGridLayout()
        # action_layout.setSpacing(0)
        action_panel.setLayout(action_layout)

        # Create button for Arming
        self._arm_btn = QPushButton("Arm")
        self._arm_btn.clicked.connect(self._arm)

        # Create buttons for Takeoff 
        self._takeoff_btn = QPushButton("Takeoff")
        self._takeoff_btn.clicked.connect(self._takeoff)

        # Create buttons for Landing
        self._land_btn = QPushButton("Land")
        self._land_btn.clicked.connect(self._land)
        
        # Create button for RTL (Return to Launch)
        self._rtl_btn = QPushButton("RTL")
        self._rtl_btn.clicked.connect(self._return_to_launch)
        
        # Create button for Hover Mode
        self._hover_btn = QPushButton("Hover")
        self._hover_btn.clicked.connect(self._toggle_hover)

        # Create Virtual Joystick for controlling altitude and yaw
        self._left_joystick = JoystickParameter(
            "Left Joystick",
            {
                "size": 120,
                "dead_zone": 0.1,
                "dead_zone_x" : 0.1,
                "dead_zone_y" : 0.1,
                "exponential_x": 0.0,
                "exponential_y": 0,
                "update_frequency": 10.0,
            }
        )
        self._left_joystick.register_callback(self._on_left_joystick_moved)

        self._right_joystick = JoystickParameter(
            "Right Joystick",
            {

                "size": 120,
                "dead_zone": 0.1,
                "dead_zone_x" : 0.1,
                "dead_zone_y" : 0.1,
                "exponential_x": 50,
                "exponential_y": 50,
                "update_frequency": 10.0,
            }
        )
        self._right_joystick.register_callback(self._on_right_joystick_moved)

        # Create labels for joystick functions
        self._left_joystick_label = QLabel("Throttle/Yaw")
        self._left_joystick_label.setAlignment(Qt.AlignCenter)
        self._right_joystick_label = QLabel("Pitch/Roll")
        self._right_joystick_label.setAlignment(Qt.AlignCenter)

        # Add Gimbal control with three rotation parameters for roll, pitch, yaw
        from pyqt_live_tuner.parameters.rotation_parameter import RotationParameter
        
        # Create a group box for gimbal controls
        gimbal_group = LinkedParameterGroup("Gimbal Control",{"layout": "horizontal"})
        
        # Create rotation parameters for roll, pitch, and yaw
        self._gimbal_roll = RotationParameter(
            "Roll",
            {
                "show_label": True,
                "label_position": "top",
                "size": 100,
                "zero_orientation": "top",
                "use_180_convention": True,
                "auto_return": False,
                "min_angle": -180,
                "max_angle": 180,
                "initial": 0,
                "snap": True,
                "snap_angles": [0, -90, 90, 180, -180],
                "snap_threshold": 5.0
            }
        )
        # self._gimbal_roll.set_label_position("bottom")
        gimbal_group.add_parameter(self._gimbal_roll)
        
        self._gimbal_pitch = RotationParameter(
            "Pitch",
            {
                "show_label": True,
                "label_position": "top",
                "size": 100,
                "zero_orientation": "top",
                "use_180_convention": True,
                "auto_return": False,
                "min_angle": -90,
                "max_angle": 90,
                "initial": 0,
                "snap": True,
                "snap_angles": [0, -45, 45, -90, 90],
                "snap_threshold": 5.0
            }
        )
        # self._gimbal_pitch.set_label_position("bottom")
        gimbal_group.add_parameter(self._gimbal_pitch)
        
        self._gimbal_yaw = RotationParameter(
            "Yaw",
            {
                "show_label": True,
                "label_position": "top",
                "size": 100,
                "zero_orientation": "top",
                "use_180_convention": True,
                "auto_return": False,
                "initial": 0,
                "snap": True,
                "snap_angles": [0, 90, -90, 180, -180],
                "snap_threshold": 5.0
            }
        )
        # self._gimbal_yaw.set_label_position("bottom")
        gimbal_group.add_parameter(self._gimbal_yaw)
        gimbal_group.register_callback(self._on_gimbal_changed)
    

        action_layout.addWidget(self._arm_btn, 0, 0)    
        action_layout.addWidget(self._takeoff_btn, 1, 0)
        action_layout.addWidget(self._land_btn, 2, 0)
        action_layout.addWidget(self._rtl_btn, 3, 0)
        action_layout.addWidget(self._hover_btn, 4, 0)  # Add hover button

        # # Add spacing between columns
        # action_layout.setColumnMinimumWidth(1, 100)  # Set minimum width for column 1
        # action_layout.setColumnMinimumWidth(2, 100)  # Set minimum width for column 2
        # action_layout.setHorizontalSpacing(20)  # Add horizontal spacing between columns

        action_layout.addWidget(self._left_joystick, 0, 1, 4, 1)
        action_layout.addWidget(self._right_joystick, 0, 2, 4, 1)
        # Add labels below joysticks
        action_layout.addWidget(self._left_joystick_label, 4, 1)
        action_layout.addWidget(self._right_joystick_label, 4, 2)
        
        # Add gimbal control at the bottom
        action_layout.addWidget(gimbal_group, 5, 0, 1, 3)

        self.main_window.add_panel(action_panel, (3, 2), row_span=1, col_span=1)

    def _setup_camera_panel(self):
        """Set up the camera settings panel."""

        self._attached_cameras = [
            "front_center",
            "back_center",
            "bottom_center"
        ]

        # Create a camera settings panel
        camera_panel = QGroupBox("Camera Settings")
        camera_layout = QVBoxLayout()
        # camera_layout.setSpacing(5)
        camera_panel.setLayout(camera_layout)
        
        # Add camera name parameter with label in horizontal layout
        camera_layout_name = QHBoxLayout()
        camera_layout_name.setContentsMargins(0, 0, 0, 0)
        camera_layout_name.setSpacing(0)


        camera_label = QLabel("Camera Name:")
        camera_layout_name.addWidget(camera_label)
        
        self.camera_name_dropdown = DropdownParameter("", {
            "options": [ x for x in self._attached_cameras],
            "initial": "front_center"
        })
        self.camera_name_dropdown.register_callback(self._on_camera_name_changed)
        camera_layout_name.addWidget(self.camera_name_dropdown)
        camera_layout.addLayout(camera_layout_name)
        
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
        self._camera_pos = LinkedParameterGroup("Camera Pose", {"layout": "vertical"})
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
            "step": 1.0,
            "initial": 5.0
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
        
        # add vertical spacer to the focus panel
        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        focus_layout.addSpacerItem(spacer)


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

        lens_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))

        
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

        filmback_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        # Tab 5: Distortion Parameters
        distortion_tab = QWidget()
        distortion_layout = QVBoxLayout()
        distortion_tab.setLayout(distortion_layout)
        
        # K1 distortion
        k1_layout = QHBoxLayout()
        k1_label = QLabel("K1:")
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
        p1_label = QLabel("P1:")
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
        p2_label = QLabel("P2:")
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
        distortion_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding))
        
        # Add tabs to tab widget
        tabs.addTab(position_tab, "Pos")
        tabs.addTab(focus_tab, "Focus")
        tabs.addTab(lens_tab, "Lens")
        tabs.addTab(filmback_tab, "Filmback")
        tabs.addTab(distortion_tab, "Distortion")
        camera_layout.addWidget(tabs)
                
       
        # add vertical spacer to the camera panel
        spacer = QSpacerItem(20, 40, QSizePolicy.Expanding, QSizePolicy.Expanding)
        camera_layout.addItem(spacer)

        # Add camera panel to the horizontal scroll layout
        self.scroll_layout.addWidget(camera_panel)
        
        # Add the system parameters scroll area to the main window
        system_parameters_container = QGroupBox("System Parameters")
        system_parameters_container.setMaximumWidth(400)
        system_parameters_container.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)


        system_parameters_layout = QVBoxLayout()
        system_parameters_layout.addWidget(self.system_parameters_scroll_area)
        
        system_parameters_container.setLayout(system_parameters_layout)
        
        # Add panel to window
        self.main_window.add_panel(system_parameters_container, (0, 1), row_span=4, col_span=1)
    
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
            
            # Map x to yaw rate (left/right rotation) - 
            # Map y to throttle (up/down movement) - 
            yaw_rate =   x * 50.0  
            throttle = - y * 10.0    
            
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
                    self.client.moveByVelocityBodyFrameAsync(
                        0,  # No horizontal movement
                        0,  # No horizontal movement
                        throttle,  # Maintain altitude
                        0.3,  # Duration in seconds
                        airsim.DrivetrainType.MaxDegreeOfFreedom
                    )


                
                self.logger.append(f"Throttle: {round(throttle, 2)} m/s, Yaw: {round(yaw_rate, 2)} deg/s")
        except Exception as e:
            self.logger.append(f"Failed to apply throttle/yaw control: {str(e)}")
    
    def _on_right_joystick_moved(self, _, pos):
        """Handle right joystick movement (pitch and roll)."""
        if not self.is_connected or self._keyboard_pressed:
            return
            
        try:
            # Extract joystick position (normalized between -1 and 1)
            x, y = pos
            
            # Map x to roll (left/right movement)
            # Map y to pitch (forward/backward movement)
            vx = (y * 5.0)     # Forward/backward velocity (y-axis of joystick)
            vy = (x * 5.0)     # Left/right velocity (x-axis of joystick)

            # Get current altitude to maintain during movement
            current_state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            current_z = current_state.kinematics_estimated.position.z_val
            current_yaw = airsim.quaternion_to_euler_angles(current_state.kinematics_estimated.orientation)[2]
            current_yaw = math.degrees(current_yaw)  # Convert to degrees
            # Apply velocity-based control while maintaining altitude

                # Use moveByVelocityZAsync for better control
            self.client.moveByVelocityBodyFrameAsync(
                vx,              # x velocity (forward/backward)
                vy,              # y velocity (left/right)
                0.0,
                0.5,
                airsim.DrivetrainType.MaxDegreeOfFreedom,
                yaw_mode=airsim.YawMode(False, current_yaw)
            )
            self.logger.append(f"Velocity X: {round(vx, 2)} m/s, Velocity Y: {round(vy, 2)} m/s")
        except Exception as e:
            self.logger.append(f"Failed to apply velocity control: {str(e)}")
    
    def _on_camera_fov_changed(self):
        """Handle camera FOV change."""
        if not self.is_connected:
            return
        
        try:
            fov = self.cam_fov.value
            self.client.simSetCameraFov(self.camera_name_dropdown.value, fov, vehicle_name=self.vehicle_name.value)
            self.logger.append(f"Camera FOV set to: {fov} degrees")
        except Exception as e:
            self.logger.append(f"Failed to set camera FOV: {e}")
    
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
                self.camera_name_dropdown.value,
                camera_pose,
                vehicle_name=self.vehicle_name.value
            )
            
            self.logger.append(f"Camera position set to: X={x:.1f}, Y={y:.1f}, Z={z:.1f}, Roll={roll:.1f}, Pitch={pitch:.1f}, Yaw={yaw:.1f}")
        except Exception as e:
            self.logger.append(f"Failed to set camera pose: {e}")

    def _sync_with_camera_panel(self):
        """Synchronize camera position between parameters panel and camera panel."""
        if not self.is_connected:
            return
        
        try:
            # Get current camera position from the camera panel
            camera_info = self.client.simGetCameraInfo(
                self.camera_name_dropdown.value,
                vehicle_name=self.vehicle_name.value
            )
            
            if camera_info:
                # Get position
                x = camera_info.pose.position.x_val
                y = camera_info.pose.position.y_val
                z = camera_info.pose.position.z_val
                
                # Get orientation and convert to Euler angles
                q = camera_info.pose.orientation
                roll_rad, pitch_rad, yaw_rad = airsim.quaternion_to_euler_angles(q)
                
                # Convert to degrees
                roll = math.degrees(roll_rad)
                pitch = math.degrees(pitch_rad)
                yaw = math.degrees(yaw_rad)
                
                # Update parameter panel controls
                self._camera_pos_x.set_value(x)
                self._camera_pos_y.set_value(y)
                self._camera_pos_z.set_value(z)
                self._camera_pos_roll.set_value(roll)
                self._camera_pos_pitch.set_value(pitch)
                self._camera_pos_yaw.set_value(yaw)
                
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
            self.client.simSetCameraFov(self.camera_name_dropdown.value, fov, vehicle_name=self.vehicle_name.value)
            self.logger.append(f"Camera FOV set to: {fov} degrees")
        except Exception as e:
            self.logger.append(f"Failed to set camera FOV: {e}")

    def _setup_environment_panel(self):
        """Set up the environment control panel."""
        # Create a parameter panel for environment control
        
        # Create a parameter group for weather
        weather_group = ParameterGroup("Weather")
        
        # Add weather sliders
        self.rain = FloatParameter("Rain", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0, "show_label": True})
        self.snow = FloatParameter("Snow", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0, "show_label": True})
        self.leaf = FloatParameter("Leaf", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0, "show_label": True})
        self.dust = FloatParameter("Dust", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0, "show_label": True})
        self.fog = FloatParameter("Fog", {"min": 0.0, "max": 1.0, "step": 0.01, "initial": 0.0, "show_label": True})
        
        # Connect weather sliders to update function
        self.rain.register_callback(self._update_weather)
        self.snow.register_callback(self._update_weather)
        self.leaf.register_callback(self._update_weather)
        self.dust.register_callback(self._update_weather)
        self.fog.register_callback(self._update_weather)
        
        # Add parameters to group
        weather_group.add_parameters([self.rain, self.snow, self.leaf, self.dust, self.fog])

        
        # Add panel to window at position (0, 1)
        self.main_window.add_panel(weather_group, (1,1))
       
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
            self.client.moveToZAsync(self.altitude.value, 3.0)
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
        return
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
                self.camera_name_dropdown.value, 
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
            distance = self.focus_distance.value * 100.0  # Convert to centimeters
            self.client.simSetFocusDistance(
                distance, 
                self.camera_name_dropdown.value, 
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
                self.camera_name_dropdown.value, 
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
                self.camera_name_dropdown.value, 
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
                    self.camera_name_dropdown.value, 
                    vehicle_name=self.vehicle_name.value
                )
                
                # self.logger.append(f"Applied lens preset: {preset} (focal length: {focal_length}mm)")
            
            # Get current preset lens settings
            current_presets = self.client.simGetPresetLensSettings(
                self.camera_name_dropdown.value, 
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
                self.camera_name_dropdown.value, 
                vehicle_name=self.vehicle_name.value
            )
            
            # Set lens preset to "Custom" when manually changing focal length
            if self.lens_preset.value != "Custom":
                self.lens_preset.dropdown.setCurrentIndex(self.lens_preset.dropdown.findText("Custom"))
            
            self.logger.append(f"Focal length set to: {focal_length}mm")
            
            # Get current field of view based on the new focal length
            try:
                current_fov = self.client.simGetCurrentFieldOfView(
                    self.camera_name_dropdown.value,
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
                    self.camera_name_dropdown.value, 
                    vehicle_name=self.vehicle_name.value
                )
                
                # self.logger.append(f"Applied filmback preset: {preset} ({width}mm x {height}mm)")
            
            # Get current preset filmback settings
            current_presets = self.client.simGetPresetFilmbackSettings(
                self.camera_name_dropdown.value, 
                vehicle_name=self.vehicle_name.value
            )
            # if current_presets:
            #     self.logger.append(f"Available filmback presets: {current_presets}")
            
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
                self.camera_name_dropdown.value, 
                vehicle_name=self.vehicle_name.value
            )
            
            if success:
                # Set filmback preset to "Custom" when manually changing sensor size
                if self.filmback_preset.value != "Custom":
                    self.filmback_preset.dropdown.setCurrentIndex(self.filmback_preset.dropdown.findText("Custom"))
                
                self.logger.append(f"Filmback size set to: {width}mm x {height}mm")
                
                # Get current filmback settings to confirm changes
                current_settings = self.client.simGetFilmbackSettings(
                    self.camera_name_dropdown.value, 
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
                self.camera_name_dropdown.value,
                distortion_params,
                vehicle_name=self.vehicle_name.value
            )
            
            self.logger.append(f"Applied camera distortion parameters: {distortion_params}")
            
            # Get current distortion parameters to confirm changes
            current_params = self.client.simGetDistortionParams(
                self.camera_name_dropdown.value, 
                vehicle_name=self.vehicle_name.value
            )
            if current_params:
                self.logger.append(f"Current distortion parameters: {current_params}")
            
        except Exception as e:
            self.logger.append(f"Failed to set distortion parameters: {e}")

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
                current_yaw = airsim.quaternion_to_euler_angles(current_state.kinematics_estimated.orientation)[2]
                
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
   
    def _on_camera_name_changed(self):
        """Handle camera name change."""
        if not self.is_connected:
            return
        
        try:
            # Update the camera name used for subsequent camera operations
            self.camera_name = self.camera_name_dropdown.value
            
            # Synchronize the gimbal controls with the new camera's orientation
            self._sync_gimbal_with_camera_pose()
            
            self.logger.append(f"Camera name set to: {self.camera_name}")
            
            # Try to refresh camera settings for the newly selected camera
            try:
                self._update_camera_settings_from_current()
            except Exception as e:
                self.logger.append(f"Could not refresh camera settings: {e}")
                
        except Exception as e:
            self.logger.append(f"Failed to update camera name: {e}")
    
    def _setup_weather_panel(self):
        """Set up the weather control panel."""
        # Create a weather settings panel
        weather_panel = QGroupBox("Weather Settings")
        weather_layout = QVBoxLayout()
        # weather_layout.setSpacing(5)
        weather_panel.setLayout(weather_layout)
        
        # Weather Enable/Disable button with checkbox
        weather_enabled_layout = QHBoxLayout()
        weather_enabled_label = QLabel("Weather Enabled:")
        weather_enabled_layout.addWidget(weather_enabled_label)
        
        self.weather_enabled = BoolParameter("", {"initial": False})
        self.weather_enabled.register_callback(self._on_weather_enabled_changed)
        weather_enabled_layout.addWidget(self.weather_enabled)
        weather_layout.addLayout(weather_enabled_layout)
        
        # Create weather parameter sliders
        # Rain
        rain_layout = QHBoxLayout()
        rain_label = QLabel("Rain:")
        rain_layout.addWidget(rain_label)
        
        self.rain = FloatParameter("", {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.rain.register_callback(self._on_weather_param_changed)
        rain_layout.addWidget(self.rain)
        weather_layout.addLayout(rain_layout)
        
        # Road Wetness
        road_wetness_layout = QHBoxLayout()
        road_wetness_label = QLabel("Road Wetness:")
        road_wetness_layout.addWidget(road_wetness_label)
        
        self.road_wetness = FloatParameter("", {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.road_wetness.register_callback(self._on_weather_param_changed)
        road_wetness_layout.addWidget(self.road_wetness)
        weather_layout.addLayout(road_wetness_layout)
        
        # Snow
        snow_layout = QHBoxLayout()
        snow_label = QLabel("Snow:")
        snow_layout.addWidget(snow_label)
        
        self.snow = FloatParameter("", {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.snow.register_callback(self._on_weather_param_changed)
        snow_layout.addWidget(self.snow)
        weather_layout.addLayout(snow_layout)
        
        # Road Snow
        road_snow_layout = QHBoxLayout()
        road_snow_label = QLabel("Road Snow:")
        road_snow_layout.addWidget(road_snow_label)
        
        self.road_snow = FloatParameter("", {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.road_snow.register_callback(self._on_weather_param_changed)
        road_snow_layout.addWidget(self.road_snow)
        weather_layout.addLayout(road_snow_layout)
        
        # Falling Leaves
        falling_leaves_layout = QHBoxLayout()
        falling_leaves_label = QLabel("Falling Leaves:")
        falling_leaves_layout.addWidget(falling_leaves_label)
        
        self.falling_leaves = FloatParameter("", {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.falling_leaves.register_callback(self._on_weather_param_changed)
        falling_leaves_layout.addWidget(self.falling_leaves)
        weather_layout.addLayout(falling_leaves_layout)
        
        # Road Leaves
        road_leaves_layout = QHBoxLayout()
        road_leaves_label = QLabel("Road Leaves:")
        road_leaves_layout.addWidget(road_leaves_label)
        
        self.road_leaves = FloatParameter("", {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.road_leaves.register_callback(self._on_weather_param_changed)
        road_leaves_layout.addWidget(self.road_leaves)
        weather_layout.addLayout(road_leaves_layout)
        
        # Dust
        dust_layout = QHBoxLayout()
        dust_label = QLabel("Dust:")
        dust_layout.addWidget(dust_label)
        
        self.dust = FloatParameter("", {
            "min": 0.0,
            "max": 1.0,
            "step":  0.01,
            "initial": 0.0
        })
        self.dust.register_callback(self._on_weather_param_changed)
        dust_layout.addWidget(self.dust)
        weather_layout.addLayout(dust_layout)
        
        # Fog
        fog_layout = QHBoxLayout()
        fog_label = QLabel("Fog:")
        fog_layout.addWidget(fog_label)
        
        self.fog = FloatParameter("", {
            "min": 0.0,
            "max": 1.0,
            "step": 0.01,
            "initial": 0.0
        })
        self.fog.register_callback(self._on_weather_param_changed)
        fog_layout.addWidget(self.fog)
        weather_layout.addLayout(fog_layout)
        
        # Wind Direction Group
        wind_group = QGroupBox("Wind Direction")
        wind_layout = QVBoxLayout()
        wind_group.setLayout(wind_layout)
        
        # Wind X direction
        wind_x_layout = QHBoxLayout()
        wind_x_label = QLabel("X:")
        wind_x_layout.addWidget(wind_x_label)
        
        self.wind_x = FloatParameter("", {
            "min": -10.0,
            "max": 10.0,
            "step": 0.1,
            "initial": 0.0
        })
        self.wind_x.register_callback(self._on_wind_direction_changed)
        wind_x_layout.addWidget(self.wind_x)
        wind_layout.addLayout(wind_x_layout)
        
        # Wind Y direction
        wind_y_layout = QHBoxLayout()
        wind_y_label = QLabel("Y:")
        wind_y_layout.addWidget(wind_y_label)
        
        self.wind_y = FloatParameter("", {
            "min": -10.0,
            "max": 10.0,
            "step": 0.1,
            "initial": 0.0
        })
        self.wind_y.register_callback(self._on_wind_direction_changed)
        wind_y_layout.addWidget(self.wind_y)
        wind_layout.addLayout(wind_y_layout)
        
        # Wind Z direction
        wind_z_layout = QHBoxLayout()
        wind_z_label = QLabel("Z:")
        wind_z_layout.addWidget(wind_z_label)
        
        self.wind_z = FloatParameter("", {
            "min": -10.0,
            "max": 10.0,
            "step": 0.1,
            "initial": 0.0
        })
        self.wind_z.register_callback(self._on_wind_direction_changed)
        wind_z_layout.addWidget(self.wind_z)
        wind_layout.addLayout(wind_z_layout)
        
        # Add wind group to weather panel
        weather_layout.addWidget(wind_group)
        

        # Add Spacer to weather panel
        vertical_spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        weather_layout.addItem(vertical_spacer)

        # Add weather panel to the horizontal scroll layout
        self.scroll_layout.addWidget(weather_panel)

    def _on_weather_enabled_changed(self):
        """Handle weather enable/disable toggle."""
        if not self.is_connected:
            return
        
        try:
            weather_enabled = self.weather_enabled.value
            if weather_enabled:
                # Enable weather and apply current weather parameters
                self._apply_all_weather_params()
                self.client.simEnableWeather(True)
                self.logger.append("Weather effects enabled")
            else:
                # Reset all weather parameters to zero
                self._reset_weather_params()
                self.client.simEnableWeather(False)
                self.logger.append("Weather effects disabled")
        except Exception as e:
            self.logger.append(f"Failed to toggle weather: {e}")
    
    def _on_weather_param_changed(self):
        """Handle changes to any weather parameter."""
        if not self.is_connected or not self.weather_enabled.value:
            return
        
        try:
            self._apply_all_weather_params()
        except Exception as e:
            self.logger.append(f"Failed to update weather parameters: {e}")
    
    def _on_wind_direction_changed(self):
        """Handle changes to wind direction parameters."""
        if not self.is_connected or not self.weather_enabled.value:
            return
        
        try:
            x = self.wind_x.value
            y = self.wind_y.value
            z = self.wind_z.value
            
            # Set the wind direction vector in AirSim
            self.client.simSetWind(airsim.Vector3r(x, y, z))
            self.logger.append(f"Wind direction set to: X={x}, Y={y}, Z={z}")
        except Exception as e:
            self.logger.append(f"Failed to set wind direction: {e}")
    
    def _apply_all_weather_params(self):
        """Apply all current weather parameters to AirSim."""
        if not self.is_connected:
            return
        
        try:
            # Set weather parameters
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Rain, self.rain.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Roadwetness, self.road_wetness.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Snow, self.snow.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.RoadSnow, self.road_snow.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.MapleLeaf, self.falling_leaves.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.RoadLeaf, self.road_leaves.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Dust, self.dust.value)
            self.client.simSetWeatherParameter(airsim.WeatherParameter.Fog, self.fog.value)
            
            # Set wind direction
            x = self.wind_x.value
            y = self.wind_y.value
            z = self.wind_z.value
            self.client.simSetWind(airsim.Vector3r(x, y, z))
            
            self.logger.append("Weather parameters applied")
        except Exception as e:
            self.logger.append(f"Failed to apply weather parameters: {e}")
    
    def _reset_weather_params(self):
        """Reset all weather parameters to zero."""
        if not self.is_connected:
            return
        
        try:
            # Reset all weather parameters to zero
            for param in [
                airsim.WeatherParameter.Rain,
                airsim.WeatherParameter.Snow,
                airsim.WeatherParameter.Leaf,
                airsim.WeatherParameter.Dust,
                airsim.WeatherParameter.Fog
            ]:
                self.client.simSetWeatherParameter(param, 0)
            
            # Reset wind
            self.client.simSetWind(airsim.Vector3r(0, 0, 0))
            
            self.logger.append("All weather parameters reset to zero")
        except Exception as e:
            self.logger.append(f"Failed to reset weather parameters: {e}")
    
    def _setup_drone_status_panel(self):
        """Set up a simple drone status panel."""
        # Create drone status panel
        drone_status_panel = QGroupBox("Drone Status")
        drone_status_panel.setMaximumHeight(130)
        drone_status_panel.setMaximumWidth(330)
        drone_status_layout = QGridLayout()
        # drone_status_layout.setSpacing(5)
        drone_status_panel.setLayout(drone_status_layout)

        # Position
        drone_status_layout.addWidget(QLabel("Position:"), 0, 0)
        self.position_label = QLabel("X: 0.00  Y: 0.00  Z: 0.00 m")
        self.position_label.setStyleSheet("color: #27ae60;")  # Blue color
        # self.position_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        drone_status_layout.addWidget(self.position_label, 0, 1)
        
        # Orientation (Euler)
        drone_status_layout.addWidget(QLabel("Orientation:"), 1, 0)
        self.orientation_label = QLabel("R: 0.00  P: 0.00  Y: 0.00°")
        self.orientation_label.setStyleSheet("color: #27ae60;")  # Green color
        # self.orientation_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        drone_status_layout.addWidget(self.orientation_label, 1, 1)
        
        # Linear Velocity
        drone_status_layout.addWidget(QLabel("Linear Velocity:"), 2, 0)
        self.lin_vel_label = QLabel("X: 0.00  Y: 0.00  Z: 0.00 m/s")
        self.lin_vel_label.setStyleSheet("color: #27ae60;")  # Blue color
        # self.lin_vel_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        drone_status_layout.addWidget(self.lin_vel_label, 2, 1)
        
        # Angular Velocity
              
              
        drone_status_layout.addWidget(QLabel("Angular Velocity:"), 3, 0)
       
        self.ang_vel_label = QLabel("X: 0.00  Y: 0.00  Z: 0.00 rad/s")
        self.ang_vel_label.setStyleSheet("color: #27ae60;")  # Green color
        drone_status_layout.addWidget(self.ang_vel_label, 3, 1)
        
        # Make labels a fixed width to ensure alignment
        for label in [self.position_label, self.orientation_label, 
                      self.lin_vel_label, self.ang_vel_label]:
            label.setMinimumWidth(200)
        
        # Add panel to scroll layout
        self.main_window.add_panel(drone_status_panel, (1,0))
        
        # Create timer for updates
        self._drone_status_timer = QTimer()
        self._drone_status_timer.timeout.connect(self._update_drone_status)
        self._drone_status_timer.start(200)  # Update 5 times per second

    def _update_drone_status(self):
        """Update the drone status information."""
        if not self.is_connected:
            return
        
        try:
            # Get current state
            state = self.client.getMultirotorState(vehicle_name=self.vehicle_name.value)
            
            # Extract position, orientation (Euler angles), linear and angular velocity
            pos = state.kinematics_estimated.position
            orient = state.kinematics_estimated.orientation
            lin_vel = state.kinematics_estimated.linear_velocity
            ang_vel = state.kinematics_estimated.angular_velocity
            
            # Convert orientation from quaternion to Euler angles
            roll, pitch, yaw = airsim.quaternion_to_euler_angles(orient)
            
            # Update labels
            self.position_label.setText(f"X: {pos.x_val:.2f}  Y: {pos.y_val:.2f}  Z: {-pos.z_val:.2f} m")
            self.orientation_label.setText(f"R: {math.degrees(roll):.2f}  P: {math.degrees(pitch):.2f}  Y: {math.degrees(yaw):.2f}°")
            self.lin_vel_label.setText(f"X: {lin_vel.x_val:.2f}  Y: {lin_vel.y_val:.2f}  Z: {lin_vel.z_val:.2f} m/s")
            self.ang_vel_label.setText(f"X: {ang_vel.x_val:.2f}  Y: {ang_vel.y_val:.2f}  Z: {ang_vel.z_val:.2f} rad/s")
        except Exception as e:
            self.logger.append(f"Failed to update drone status: {e}")
            self.position_label.setText("Error")
            self.orientation_label.setText("Error")
            self.lin_vel_label.setText("Error")
            self.ang_vel_label.setText("Error")
    
    def _open_airsim_settings_editor(self):
        """Open the AirSim settings editor in a popup window."""
        try:
            from airsim_settings_editor import AirSimSettingsEditor
            
            # Create a new QApplication instance if needed
            app = QApplication.instance()
            if not app:
                app = QApplication([])
            
            # Create and show the settings editor window
            if not self.settings_editor:
                self.settings_editor = AirSimSettingsEditor()
            
            self.settings_editor.show()
            self.settings_editor.raise_()  # Bring to front
            
            self.logger.append("AirSim Settings Editor opened")
        except Exception as e:
            self.logger.append(f"Failed to open AirSim Settings Editor: {e}")
            
            # Show detailed error information to help debugging
            import traceback
            self.logger.append(traceback.format_exc())
    
    def _on_gimbal_roll_changed(self, _, value):
        """Handle gimbal roll rotation changes."""
        if not self.is_connected:
            return
        
        try:
            roll = value  # Value from rotation parameter is in degrees
            
            # Get current camera pose to preserve other values
            camera_name = self.camera_name_dropdown.value
            camera_info = self.client.simGetCameraInfo(camera_name, vehicle_name=self.vehicle_name.value)
            
            if camera_info:
                # Create new pose with updated roll but keeping other values
                new_pose = camera_info.pose
                
                # Extract current pitch and yaw from quaternion
                _, pitch_rad, yaw_rad = airsim.quaternion_to_euler_angles(new_pose.orientation)
                
                # Create new quaternion with updated roll
                roll_rad = math.radians(roll)
                new_pose.orientation = airsim.Quaternionr(roll_rad, pitch_rad, yaw_rad)
                
                # Set the camera pose with the new orientation
                self.client.simSetCameraPose(camera_name, new_pose, vehicle_name=self.vehicle_name.value)
                
                self.logger.append(f"Gimbal roll set to: {roll:.1f} degrees")
                
                # Update the camera position panel if it exists
                if hasattr(self, '_camera_pos_roll'):
                    self._camera_pos_roll.set_value(roll)
            else:
                self.logger.append(f"Failed to get camera info for {camera_name}")
        except Exception as e:
            self.logger.append(f"Failed to set gimbal roll: {e}")
         
    def _on_gimbal_changed(self, _, value):
        """Handle gimbal rotation changes."""
        if not self.is_connected:
            return
        
        try:
            roll, pitch, yaw = value["Roll"], value["Pitch"], value["Yaw"]

            new_pose =  airsim.Pose( 
                airsim.Vector3r(0, 0, 0), 
                airsim.euler_to_quaternion(math.radians(roll), math.radians(pitch), math.radians(yaw))
            )
            camera_name = self.camera_name_dropdown.value
            self.client.simSetCameraPose(camera_name, new_pose, vehicle_name=self.vehicle_name.value)
            self.logger.append(f"Gimbal set to: Roll={roll:.1f}, Pitch={pitch:.1f}, Yaw={yaw:.1f} degrees")
        except Exception as e:
            self.logger.append(f"Failed to set gimbal: {e}")   
    
    def _sync_gimbal_with_camera_pose(self):
        """Synchronize gimbal rotation widgets with current camera pose."""
        if not self.is_connected:
            return
        
        try:
            # Get current camera info
            camera_name = self.camera_name_dropdown.value
            camera_info = self.client.simGetCameraInfo(camera_name, vehicle_name=self.vehicle_name.value)
            
            if camera_info:
                # Extract Euler angles from quaternion
                q = camera_info.pose.orientation
                roll_rad, pitch_rad, yaw_rad = airsim.quaternion_to_euler_angles(q)
                
                # Convert to degrees
                roll = math.degrees(roll_rad)
                pitch = math.degrees(pitch_rad)
                yaw = math.degrees(yaw_rad)
                
                # Update gimbal rotation widgets without triggering callbacks
                self._gimbal_roll.set_value(roll)
                self._gimbal_pitch.set_value(pitch)
                self._gimbal_yaw.set_value(yaw)
                
                self.logger.append(f"Synchronized gimbal controls with camera pose")
            else:
                self.logger.append(f"Failed to get camera info for {camera_name}")
        except Exception as e:
            self.logger.append(f"Failed to sync gimbal with camera pose: {e}")
    
    def _setup_image_display(self):
        """Set up the image display panel for multi-camera viewing.
        
        This method creates a panel that can display multiple camera views
        from AirSim simultaneously.
        """
        # Create a panel for camera views
        camera_view_panel = QGroupBox("Camera Views")
        camera_view_panel.setContentsMargins(0, 0, 0, 0)
        camera_view_layout = QGridLayout()
        camera_view_layout.setContentsMargins(0, 0, 0, 0)
        camera_view_layout.setSpacing(0)

        camera_view_panel.setLayout(camera_view_layout)
        
        self._image_displays = {}
        
        # Create main camera display 
        front_center = ImageDisplay(config={

            "title": "Front Camera",
            "size": (400, 300),
            "maintain_aspect_ratio": False,
            "show_title": True
        })
        camera_view_layout.addWidget(front_center, 0, 0, 1, 2)
        self._image_displays["front_center"] = front_center

        back_center = ImageDisplay(config={
            "title": "Back Camera",
            "size": (256, 144),
            "maintain_aspect_ratio": False,
            "show_title": True
        })
        camera_view_layout.addWidget(back_center, 1, 0, 1, 1)
        self._image_displays["back_center"] = back_center

        bottom_center = ImageDisplay(config={
            "title": "Bottom Camera",
            "size": (256, 144),
            "maintain_aspect_ratio": False,
            "show_title": True
        })
        camera_view_layout.addWidget(bottom_center, 1, 1, 1, 1)
        self._image_displays["bottom_center"] = bottom_center
        self.main_window.add_panel(camera_view_panel, (0, 2), row_span=3)

        # Create a Timer to update camera images
        self._camera_update_timer = QTimer()
        self._camera_update_timer.timeout.connect(self._update_camera_images)
        self._camera_update_timer.start(100)  # Update every 100 ms

    def _update_camera_images(self):
        """Update all camera images in the grid."""
        if not self.is_connected or not self._image_displays:
            return
        
        try:
            # Create image requests for all active cameras
            requests = []
            camera_type_map = {
                "Scene": airsim.ImageType.Scene,
                "Depth": airsim.ImageType.DepthVis,
                "Segmentation": airsim.ImageType.Segmentation,
                "Normals": airsim.ImageType.SurfaceNormals
            }
            
            # Get current camera type from dropdown
            camera_type = camera_type_map.get(self.cam_type.value, airsim.ImageType.Scene)
            
            for camera_name in self._attached_cameras:
                requests.append(airsim.ImageRequest(
                    camera_name, 
                    camera_type, 
                    False, 
                    False
                ))
            
            # Get images for all cameras in a single request
            if requests:
                responses = self.client.simGetImages(requests, vehicle_name=self.vehicle_name.value)
                
                # Process each response
                for i, response in enumerate(responses):
                    if response.pixels_as_float or response.compress:
                        # Skip unsupported formats for simplicity
                        continue
                    
                    # Get corresponding camera name
                    camera_name = self._attached_cameras[i]
                    
                    # Convert image data to numpy array
                    img1d = np.fromstring(response.image_data_uint8, dtype=np.uint8)
                    
                    try:
                        # Determine if this is an RGB or RGBA image based on array size
                        total_pixels = len(img1d)
                        
                        # Check if we have explicit dimensions from the response
                        if hasattr(response, 'width') and hasattr(response, 'height'):
                            width = response.width
                            height = response.height
                            channels = total_pixels // (width * height)
                            
                            if channels not in [3, 4]:
                                # Unexpected channel count, recalculate dimensions
                                self.logger.append(f"Unexpected channel count: {channels} for {camera_name}")
                                channels = 4  # Assume RGBA as default
                            
                            # Verify if the dimensions are correct
                            if width * height * channels != total_pixels:
                                self.logger.append(f"Dimension mismatch: {width}x{height}x{channels} != {total_pixels}")
                                # Need to recalculate dimensions
                                width = height = None
                        else:
                            width = height = None
                            channels = 4  # Assume RGBA by default
                        
                        # If we need to calculate dimensions
                        if width is None or height is None:
                            # Check common channel counts (RGB or RGBA)
                            if total_pixels % 3 == 0:  # Could be RGB
                                channels = 3
                                total_pixels_rgb = total_pixels // 3
                                # Try to determine height and width for RGB
                                # Assuming common aspect ratios like 16:9, 4:3, etc.
                                if camera_name == "front_center":
                                    # For front camera, try 16:9 aspect ratio
                                    height = int(np.sqrt(total_pixels_rgb * 9 / 16))
                                    width = total_pixels_rgb // height
                                else:
                                    # For other cameras, try 16:9 or 4:3 ratios
                                    # First try 16:9
                                    height = int(np.sqrt(total_pixels_rgb * 9 / 16))
                                    width = total_pixels_rgb // height
                                    
                                    # If dimensions don't match up, try 4:3
                                    if width * height != total_pixels_rgb:
                                        height = int(np.sqrt(total_pixels_rgb * 3 / 4))
                                        width = total_pixels_rgb // height
                            
                            elif total_pixels % 4 == 0:  # Could be RGBA
                                channels = 4
                                total_pixels_rgba = total_pixels // 4
                                # Try to determine height and width for RGBA
                                if camera_name == "front_center":
                                    # For front camera, try 16:9 aspect ratio
                                    height = int(np.sqrt(total_pixels_rgba * 9 / 16))
                                    width = total_pixels_rgba // height
                                else:
                                    # For other cameras, try 16:9 or 4:3 ratios
                                    # First try 16:9
                                    height = int(np.sqrt(total_pixels_rgba * 9 / 16))
                                    width = total_pixels_rgba // height
                                    
                                    # If dimensions don't match up, try 4:3
                                    if width * height != total_pixels_rgba:
                                        height = int(np.sqrt(total_pixels_rgba * 3 / 4))
                                        width = total_pixels_rgba // height
                            else:
                                # If not divisible by 3 or 4, probably a custom format
                                self.logger.append(f"Unusual image format for {camera_name}, size: {total_pixels}")
                                # As a fallback, try a simple square shape
                                channels = 1
                                height = int(np.sqrt(total_pixels))
                                width = height
                        
                        # Print the dimensions we're using
                        # self.logger.append(f"{camera_name}: Using dimensions {width}x{height}x{channels}")
                        
                        # Make sure the reshape will work with these dimensions
                        if width * height * channels == total_pixels:
                            if channels == 4:
                                img = img1d.reshape(height, width, 4)
                                # Display the image
                                if camera_name in self._image_displays:
                                    self._image_displays[camera_name].display_image(img)
                            elif channels == 3:
                                # For RGB images, reshape and convert to RGBA for display
                                img = img1d.reshape(height, width, 3)
                                # Convert RGB to RGBA by adding an alpha channel
                                img_rgba = np.zeros((height, width, 4), dtype=np.uint8)
                                img_rgba[:,:,0:3] = img
                                img_rgba[:,:,3] = 255  # Fully opaque
                                # Display the image
                                if camera_name in self._image_displays:
                                    self._image_displays[camera_name].display_image(img_rgba)
                            else:
                                # Single channel image (grayscale)
                                img = img1d.reshape(height, width)
                                # Convert to RGBA by duplicating to RGB channels
                                img_rgba = np.zeros((height, width, 4), dtype=np.uint8)
                                img_rgba[:,:,0] = img_rgba[:,:,1] = img_rgba[:,:,2] = img
                                img_rgba[:,:,3] = 255  # Fully opaque
                                # Display the image
                                if camera_name in self._image_displays:
                                    self._image_displays[camera_name].display_image(img_rgba)
                        else:
                            self.logger.append(f"Dimension calculation failed for {camera_name}: {width}x{height}x{channels} != {total_pixels}")
                    except Exception as reshape_err:
                        self.logger.append(f"Failed to reshape image for {camera_name}: {reshape_err}")
        except Exception as e:
            self.logger.append(f"Failed to update camera images: {e}")


    def append(self, message):
        """Append a message to the logger and auto-scroll to bottom."""
        # Append the message to the logger
        self.logger.append(message)
        
        # Auto-scroll to the bottom
        cursor = self.logger.textCursor()
        cursor.movePosition(cursor.End)
        self.logger.setTextCursor(cursor)
        self.logger.ensurePolished()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AirSimGUI()
    window.run()