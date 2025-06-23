#!/usr/bin/env python3
"""
AirSim Settings Editor - A specialized GUI for editing AirSim settings files.
This editor combines a general-purpose JSON editor with AirSim-specific knowledge
to provide a more user-friendly editing experience.
"""

import sys
import json
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                            QWidget, QLabel, QComboBox, QPushButton, QFileDialog,
                            QTabWidget, QMessageBox, QSplitter, QTreeView, QFrame,
                            QInputDialog, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

# Import our JSON editor widget
from json_editor import JsonEditorWidget

# Import AirSim settings types
from airsim_settings_types import (
    AirSimSettings, VehicleSetting, CameraSettingVechile, CameraDirectorSetting,
    Vector3r, Rotation, Pose, OriginGeopoint, TimeOfDaySetting
)

class AirSimSettingsEditor(QMainWindow):
    """Main AirSim Settings Editor window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('AirSim Settings Editor')
        self.setGeometry(100, 100, 1280, 800)
        
        self.current_file = None
        self.settings = None
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the main UI components."""
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Add toolbar at the top
        toolbar_layout = QHBoxLayout()
        
        # File operations
        new_button = QPushButton("New")
        new_button.clicked.connect(self.new_file)
        toolbar_layout.addWidget(new_button)
        
        open_button = QPushButton("Open")
        open_button.clicked.connect(self.open_file)
        toolbar_layout.addWidget(open_button)
        
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_file)
        toolbar_layout.addWidget(save_button)
        
        save_as_button = QPushButton("Save As")
        save_as_button.clicked.connect(self.save_file_as)
        toolbar_layout.addWidget(save_as_button)
        
        # Add defaults button
        generate_defaults_button = QPushButton("Generate Defaults")
        generate_defaults_button.clicked.connect(self.generate_defaults)
        toolbar_layout.addWidget(generate_defaults_button)
        
        toolbar_layout.addStretch()
        
        # SimMode selector
        sim_mode_label = QLabel("Simulation Mode:")
        toolbar_layout.addWidget(sim_mode_label)
        
        self.sim_mode_combo = QComboBox()
        self.sim_mode_combo.addItems(["Multirotor", "Car", "ComputerVision"])
        self.sim_mode_combo.currentTextChanged.connect(self.on_sim_mode_changed)
        toolbar_layout.addWidget(self.sim_mode_combo)
        
        main_layout.addLayout(toolbar_layout)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        
        # JSON Editor Tab
        self.json_editor_tab = QWidget()
        json_editor_layout = QVBoxLayout(self.json_editor_tab)
        
        self.json_editor = JsonEditorWidget()
        self.json_editor.jsonChanged.connect(self.on_json_changed)
        json_editor_layout.addWidget(self.json_editor)
        
        # Set wider column widths for the tree view in the JSON editor
        self.set_tree_column_widths(self.json_editor.tree)
        
        self.tab_widget.addTab(self.json_editor_tab, "JSON Editor")
        
        # Vehicles Tab
        self.vehicles_tab = QWidget()
        vehicles_layout = QVBoxLayout(self.vehicles_tab)
        
        # Vehicles toolbar
        vehicles_toolbar = QHBoxLayout()
        
        vehicle_label = QLabel("Vehicle:")
        vehicles_toolbar.addWidget(vehicle_label)
        
        self.vehicle_combo = QComboBox()
        self.vehicle_combo.currentTextChanged.connect(self.on_vehicle_changed)
        vehicles_toolbar.addWidget(self.vehicle_combo)
        
        add_vehicle_button = QPushButton("Add Vehicle")
        add_vehicle_button.clicked.connect(self.add_vehicle)
        vehicles_toolbar.addWidget(add_vehicle_button)
        
        remove_vehicle_button = QPushButton("Remove Vehicle")
        remove_vehicle_button.clicked.connect(self.remove_vehicle)
        vehicles_toolbar.addWidget(remove_vehicle_button)
        
        vehicles_toolbar.addStretch()
        
        vehicles_layout.addLayout(vehicles_toolbar)
        
        # Vehicle editor using a specialized JSON editor
        self.vehicle_editor = JsonEditorWidget()
        self.vehicle_editor.jsonChanged.connect(self.on_vehicle_json_changed)
        vehicles_layout.addWidget(self.vehicle_editor)
        
        # Set wider column widths for the vehicle editor tree view
        self.set_tree_column_widths(self.vehicle_editor.tree)
        
        self.tab_widget.addTab(self.vehicles_tab, "Vehicles")
        
        # Cameras Tab
        self.cameras_tab = QWidget()
        cameras_layout = QVBoxLayout(self.cameras_tab)
        
        # Cameras toolbar
        cameras_toolbar = QHBoxLayout()
        
        camera_vehicle_label = QLabel("Vehicle:")
        cameras_toolbar.addWidget(camera_vehicle_label)
        
        self.camera_vehicle_combo = QComboBox()
        self.camera_vehicle_combo.currentTextChanged.connect(self.on_camera_vehicle_changed)
        cameras_toolbar.addWidget(self.camera_vehicle_combo)
        
        camera_label = QLabel("Camera:")
        cameras_toolbar.addWidget(camera_label)
        
        self.camera_combo = QComboBox()
        self.camera_combo.currentTextChanged.connect(self.on_camera_changed)
        cameras_toolbar.addWidget(self.camera_combo)
        
        add_camera_button = QPushButton("Add Camera")
        add_camera_button.clicked.connect(self.add_camera)
        cameras_toolbar.addWidget(add_camera_button)
        
        remove_camera_button = QPushButton("Remove Camera")
        remove_camera_button.clicked.connect(self.remove_camera)
        cameras_toolbar.addWidget(remove_camera_button)
        
        cameras_toolbar.addStretch()
        
        cameras_layout.addLayout(cameras_toolbar)
        
        # Camera editor using a specialized JSON editor
        self.camera_editor = JsonEditorWidget()
        self.camera_editor.jsonChanged.connect(self.on_camera_json_changed)
        cameras_layout.addWidget(self.camera_editor)
        
        # Set wider column widths for the camera editor tree view
        self.set_tree_column_widths(self.camera_editor.tree)
        
        self.tab_widget.addTab(self.cameras_tab, "Cameras")
        
        # Add tabs widget to main layout
        main_layout.addWidget(self.tab_widget)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        self.setCentralWidget(central_widget)
        
        # Initialize with default settings
        self.new_file()
    
    def set_tree_column_widths(self, tree_view):
        """Set wider column widths for a tree view."""
        header = tree_view.header()
        header.setStretchLastSection(False)
        header.resizeSection(0, 300)  # Key column - 300 pixels wide
        header.resizeSection(1, 400)  # Value column - 400 pixels wide
        header.resizeSection(2, 100)  # Type column - 100 pixels wide
    
    def new_file(self):
        """Create new AirSim settings with defaults."""
        self.settings = AirSimSettings(sim_mode="Multirotor")
        self.current_file = None
        self.json_editor.set_json(self.settings.to_dict())
        self.sim_mode_combo.setCurrentText(self.settings.SimMode)
        self.update_vehicle_list()
        self.update_camera_vehicle_list()
        self.update_title()
        self.statusBar().showMessage("New settings file created")
    
    def open_file(self):
        """Open an existing AirSim settings file."""
        path, _ = QFileDialog.getOpenFileName(
            self, 'Open AirSim Settings', '', 
            'JSON Files (*.json);;All Files (*)'
        )
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    settings_dict = json.load(f)
                
                self.settings = AirSimSettings.from_dict(settings_dict)
                self.current_file = path
                self.json_editor.set_json(settings_dict)
                
                # Update UI elements
                self.sim_mode_combo.setCurrentText(self.settings.SimMode)
                self.update_vehicle_list()
                self.update_camera_vehicle_list()
                
                self.update_title()
                self.statusBar().showMessage(f"Opened: {path}")
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to open file:\n{str(e)}')
    
    def save_file(self):
        """Save the current settings to file."""
        if self.current_file:
            self.save_to_file(self.current_file)
        else:
            self.save_file_as()
    
    def save_file_as(self):
        """Save the current settings to a new file."""
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save AirSim Settings', '', 
            'JSON Files (*.json);;All Files (*)'
        )
        if path:
            if not path.endswith('.json'):
                path += '.json'
            self.save_to_file(path)
    
    def save_to_file(self, path):
        """Save settings to specified file path."""
        try:
            # Get current JSON data from editor
            settings_dict = self.json_editor.get_json()
            
            # Update the settings object from the JSON
            self.settings = AirSimSettings.from_dict(settings_dict)
            
            # Save to file
            with open(path, 'w') as f:
                json.dump(settings_dict, f, indent=4)
            
            self.current_file = path
            self.update_title()
            self.statusBar().showMessage(f"Saved: {path}")
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to save file:\n{str(e)}')
    
    def update_title(self):
        """Update the window title with current file."""
        title = 'AirSim Settings Editor'
        if self.current_file:
            title += f' - {self.current_file}'
        if self.json_editor.is_modified:
            title += ' *'
        self.setWindowTitle(title)
    
    def on_json_changed(self, json_data):
        """Handle changes in the JSON editor."""
        self.update_title()
        
        # Try to update settings object
        try:
            self.settings = AirSimSettings.from_dict(json_data)
            
            # Update UI elements without triggering additional changes
            if self.settings.SimMode != self.sim_mode_combo.currentText():
                self.sim_mode_combo.blockSignals(True)
                self.sim_mode_combo.setCurrentText(self.settings.SimMode)
                self.sim_mode_combo.blockSignals(False)
        except Exception as e:
            # Just log the error but don't interrupt the user
            print(f"Error updating settings: {str(e)}")
    
    def on_sim_mode_changed(self, sim_mode):
        """Handle changes to the simulation mode."""
        if self.settings and sim_mode != self.settings.SimMode:
            # Get current JSON
            current_json = self.json_editor.get_json()
            
            # Update the SimMode
            current_json["SimMode"] = sim_mode
            
            # Update the JSON editor
            self.json_editor.set_json(current_json)
            
            # Update the settings object
            self.settings.SimMode = sim_mode
            
            self.statusBar().showMessage(f"Simulation mode changed to {sim_mode}")
    
    def on_vehicle_changed(self, vehicle_name):
        """Handle vehicle selection change."""
        if not self.settings or not vehicle_name:
            return
            
        # Get the vehicle setting from the dictionary
        if vehicle_name in self.settings.Vehicles:
            vehicle_setting = self.settings.Vehicles[vehicle_name]
            # Update the vehicle editor with the selected vehicle's settings
            self.vehicle_editor.set_json(vehicle_setting.to_dict())
        else:
            # Clear the vehicle editor if no valid vehicle is selected
            self.vehicle_editor.set_json({})
    
    def add_vehicle(self):
        """Add a new vehicle to the settings."""
        if not self.settings:
            return
            
        # Create a dialog to get the vehicle name
        vehicle_name, ok = QInputDialog.getText(
            self, "New Vehicle", "Enter vehicle name:", QLineEdit.Normal, "NewVehicle"
        )
        
        if ok and vehicle_name:
            # Check if the name already exists
            if vehicle_name in self.settings.Vehicles:
                QMessageBox.warning(
                    self, "Duplicate Name", 
                    f"A vehicle named '{vehicle_name}' already exists. Please choose a different name."
                )
                return
                
            # Create a default vehicle setting based on simulation mode
            vehicle_type = "SimpleFlight" if self.settings.SimMode == "Multirotor" else "PhysXCar"
            
            # Create the vehicle setting
            new_vehicle = VehicleSetting(
                vehicle_type=vehicle_type,
                default_vehicle_state="",
                auto_create=True
            )
            
            # Add to settings
            self.settings.Vehicles[vehicle_name] = new_vehicle
            
            # Update the main JSON editor
            self.json_editor.set_json(self.settings.to_dict())
            
            # Update vehicle combo box
            self.update_vehicle_list()
            
            # Select the new vehicle
            self.vehicle_combo.setCurrentText(vehicle_name)
            
            self.statusBar().showMessage(f"Added new vehicle: {vehicle_name}")
    
    def remove_vehicle(self):
        """Remove the selected vehicle from the settings."""
        if not self.settings:
            return
            
        vehicle_name = self.vehicle_combo.currentText()
        if not vehicle_name:
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f'Are you sure you want to delete the vehicle "{vehicle_name}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from settings
            if vehicle_name in self.settings.Vehicles:
                del self.settings.Vehicles[vehicle_name]
                
                # Update the main JSON editor
                self.json_editor.set_json(self.settings.to_dict())
                
                # Update vehicle combo box
                self.update_vehicle_list()
                
                self.statusBar().showMessage(f"Removed vehicle: {vehicle_name}")

    def on_vehicle_json_changed(self, json_data):
        """Handle changes in the vehicle JSON editor."""
        # Get the current vehicle name
        vehicle_name = self.vehicle_combo.currentText()
        if not self.settings or not vehicle_name:
            return
        
        # Try to update the vehicle in the settings
        try:
            # Create a vehicle setting from the JSON
            updated_vehicle = VehicleSetting.from_dict(json_data)
            
            # Update the vehicle in the settings
            self.settings.Vehicles[vehicle_name] = updated_vehicle
            
            # Update the main JSON editor
            main_json = self.json_editor.get_json()
            main_json["Vehicles"][vehicle_name] = json_data
            
            # Update without triggering signals
            self.json_editor.blockSignals(True)
            self.json_editor.set_json(main_json)
            self.json_editor.blockSignals(False)
            
            self.statusBar().showMessage(f"Updated vehicle: {vehicle_name}")
        except Exception as e:
            self.statusBar().showMessage(f"Error updating vehicle: {str(e)}")
    
    def update_vehicle_list(self):
        """Update the vehicle dropdown list based on current settings."""
        if not self.settings:
            return
            
        # Block signals to prevent triggering on_vehicle_changed
        self.vehicle_combo.blockSignals(True)
        
        # Clear the current list
        self.vehicle_combo.clear()
        
        # Add vehicles from settings
        for vehicle_name in self.settings.Vehicles.keys():
            self.vehicle_combo.addItem(vehicle_name)
            
        # Select the first vehicle if available
        if self.vehicle_combo.count() > 0:
            self.vehicle_combo.setCurrentIndex(0)
            # Update the vehicle editor with the selected vehicle
            self.on_vehicle_changed(self.vehicle_combo.currentText())
        else:
            # Clear the vehicle editor if no vehicles exist
            self.vehicle_editor.set_json({})
        
        # Re-enable signals
        self.vehicle_combo.blockSignals(False)

    def update_camera_vehicle_list(self):
        """Update the camera vehicle dropdown list based on current settings."""
        if not self.settings:
            return
            
        # Block signals to prevent triggering on_camera_vehicle_changed
        self.camera_vehicle_combo.blockSignals(True)
        
        # Clear the current list
        self.camera_vehicle_combo.clear()
        
        # Add vehicles from settings
        for vehicle_name in self.settings.Vehicles.keys():
            self.camera_vehicle_combo.addItem(vehicle_name)
            
        # Select the first vehicle if available
        if self.camera_vehicle_combo.count() > 0:
            self.camera_vehicle_combo.setCurrentIndex(0)
            # Update the camera editor with the first vehicle's cameras
            self.on_camera_vehicle_changed(self.camera_vehicle_combo.currentText())
        else:
            # Clear the camera combo box and editor if no vehicles exist
            self.camera_combo.clear()
            self.camera_editor.set_json({})
        
        # Re-enable signals
        self.camera_vehicle_combo.blockSignals(False)

    def on_camera_vehicle_changed(self, vehicle_name):
        """Handle camera vehicle selection change."""
        if not self.settings or not vehicle_name:
            return
            
        # Update the camera combo box based on the selected vehicle
        if vehicle_name in self.settings.Vehicles:
            vehicle_setting = self.settings.Vehicles[vehicle_name]
            
            # Update camera combo box
            self.camera_combo.blockSignals(True)
            self.camera_combo.clear()
            
            # Add cameras from vehicle settings
            for camera_name in vehicle_setting.Cameras.keys():
                self.camera_combo.addItem(camera_name)
            
            # Select the first camera if available
            if self.camera_combo.count() > 0:
                self.camera_combo.setCurrentIndex(0)
                # Update the camera editor with the selected camera
                self.on_camera_changed(self.camera_combo.currentText())
            else:
                # Clear the camera editor if no cameras exist
                self.camera_editor.set_json({})
            
            self.camera_combo.blockSignals(False)
        else:
            # Clear the camera combo box and editor if no valid vehicle is selected
            self.camera_combo.clear()
            self.camera_editor.set_json({})
    
    def on_camera_changed(self, camera_name):
        """Handle camera selection change."""
        vehicle_name = self.camera_vehicle_combo.currentText()
        if not self.settings or not vehicle_name or not camera_name:
            return
            
        # Get the vehicle setting
        if vehicle_name in self.settings.Vehicles:
            vehicle_setting = self.settings.Vehicles[vehicle_name]
            
            # Update the camera editor with the selected camera's settings
            if camera_name in vehicle_setting.Cameras:
                camera_setting = vehicle_setting.Cameras[camera_name]
                self.camera_editor.set_json(camera_setting.to_dict())
            else:
                self.camera_editor.set_json({})
    
    def add_camera(self):
        """Add a new camera to the selected vehicle."""
        vehicle_name = self.camera_vehicle_combo.currentText()
        if not self.settings or not vehicle_name:
            return
            
        # Create a dialog to get the camera name
        camera_name, ok = QInputDialog.getText(
            self, "New Camera", "Enter camera name:", QLineEdit.Normal, "NewCamera"
        )
        
        if ok and camera_name:
            # Check if the name already exists
            if vehicle_name in self.settings.Vehicles and camera_name in self.settings.Vehicles[vehicle_name].Cameras:
                QMessageBox.warning(
                    self, "Duplicate Name", 
                    f"A camera named '{camera_name}' already exists for this vehicle. Please choose a different name."
                )
                return
                
            # Create a default camera setting
            new_camera = CameraSettingVechile()
            
            # Add to vehicle's camera settings
            self.settings.Vehicles[vehicle_name].Cameras[camera_name] = new_camera
            
            # Update the main JSON editor
            self.json_editor.set_json(self.settings.to_dict())
            
            # Update camera combo box
            self.camera_combo.addItem(camera_name)
            self.camera_combo.setCurrentText(camera_name)
            
            self.statusBar().showMessage(f"Added new camera: {camera_name} to vehicle: {vehicle_name}")
    
    def remove_camera(self):
        """Remove the selected camera from the current vehicle."""
        vehicle_name = self.camera_vehicle_combo.currentText()
        camera_name = self.camera_combo.currentText()
        if not self.settings or not vehicle_name or not camera_name:
            return
            
        # Confirm deletion
        reply = QMessageBox.question(
            self, 'Confirm Deletion',
            f'Are you sure you want to delete the camera "{camera_name}" from vehicle "{vehicle_name}"?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Remove from vehicle's camera settings
            if vehicle_name in self.settings.Vehicles:
                vehicle_setting = self.settings.Vehicles[vehicle_name]
                if camera_name in vehicle_setting.Cameras:
                    del vehicle_setting.Cameras[camera_name]
                    
                    # Update the main JSON editor
                    self.json_editor.set_json(self.settings.to_dict())
                    
                    # Update camera combo box
                    self.camera_combo.removeItem(self.camera_combo.currentIndex())
                    
                    self.statusBar().showMessage(f"Removed camera: {camera_name} from vehicle: {vehicle_name}")

    def on_camera_json_changed(self, json_data):
        """Handle changes in the camera JSON editor."""
        vehicle_name = self.camera_vehicle_combo.currentText()
        camera_name = self.camera_combo.currentText()
        if not self.settings or not vehicle_name or not camera_name:
            return
        
        # Try to update the camera in the settings
        try:
            # Create a camera setting from the JSON
            updated_camera = CameraSettingVechile.from_dict(json_data)
            
            # Update the camera in the vehicle's settings
            self.settings.Vehicles[vehicle_name].Cameras[camera_name] = updated_camera
            
            # Update the main JSON editor
            main_json = self.json_editor.get_json()
            if "Vehicles" in main_json and vehicle_name in main_json["Vehicles"]:
                if "Cameras" not in main_json["Vehicles"][vehicle_name]:
                    main_json["Vehicles"][vehicle_name]["Cameras"] = {}
                main_json["Vehicles"][vehicle_name]["Cameras"][camera_name] = json_data
                
                # Update without triggering signals
                self.json_editor.blockSignals(True)
                self.json_editor.set_json(main_json)
                self.json_editor.blockSignals(False)
            
            self.statusBar().showMessage(f"Updated camera: {camera_name} for vehicle: {vehicle_name}")
        except Exception as e:
            self.statusBar().showMessage(f"Error updating camera: {str(e)}")
    
    def generate_defaults(self):
        """Generate default settings based on the current simulation mode."""
        # Confirm with the user
        reply = QMessageBox.question(
            self, 'Generate Default Settings',
            'This will generate default settings for your selected simulation mode.\n'
            'Any existing settings will be replaced. Continue?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Get current simulation mode
            sim_mode = self.sim_mode_combo.currentText()
            
            # Create appropriate default settings
            if sim_mode == "Multirotor":
                # Create multirotor defaults
                self.settings = AirSimSettings(
                    sim_mode="Multirotor",
                    vehicles={
                        "SimpleFlight1": VehicleSetting(
                            vehicle_type="SimpleFlight",
                            default_vehicle_state="Armed",
                            auto_create=True,
                            pose=Pose(
                                position=Vector3r(0, 0, -2),
                                rotation=Rotation(0, 0, 0)
                            )
                        )
                    }
                )
            elif sim_mode == "Car":
                # Create car defaults
                self.settings = AirSimSettings(
                    sim_mode="Car",
                    vehicles={
                        "PhysXCar1": VehicleSetting(
                            vehicle_type="PhysXCar",
                            default_vehicle_state="",
                            auto_create=True,
                            pose=Pose(
                                position=Vector3r(0, 0, 0),
                                rotation=Rotation(0, 0, 0)
                            )
                        )
                    }
                )
            elif sim_mode == "ComputerVision":
                # Create computer vision defaults (no vehicles)
                self.settings = AirSimSettings(
                    sim_mode="ComputerVision"
                )
            
            # Update the UI
            self.json_editor.set_json(self.settings.to_dict())
            self.update_vehicle_list()
            self.update_camera_vehicle_list()
            
            self.statusBar().showMessage(f"Generated default settings for {sim_mode} mode")
    
def main():
    app = QApplication(sys.argv)
    editor = AirSimSettingsEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()