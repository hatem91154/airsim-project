#!/usr/bin/env python3
"""Rotation parameter widget for PyQt Live Tuner.

This module provides a rotation dial widget and parameter for selecting angles.
"""

import math
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize
from typing import Optional, Dict, Callable, List

from .parameter import Parameter


class RotationDialWidget(QWidget):
    """Custom widget that implements the rotation dial control UI.
    
    A circular widget that allows selection of angles by rotating a dial.
    The angle is measured in degrees, with configurable range and orientation.
    
    Attributes:
        angleChanged: Signal emitted when angle changes (degrees)
        _angle: Current angle in degrees
        _pressed: Whether the dial is currently being dragged
        _origin_angle: The angle that represents the origin/zero position
        _auto_return: Whether to automatically return to origin
        _auto_return_threshold: Threshold in degrees for auto-return
        _min_angle: Minimum allowable angle
        _max_angle: Maximum allowable angle
        _use_180_convention: Whether to use -180 to 180 convention instead of 0 to 359
        _important_angles: List of important angles to highlight
    """
    
    angleChanged = pyqtSignal(float)
    
    def __init__(self, parent=None):
        """Initialize the rotation dial widget."""
        super().__init__(parent)
        
        # Set minimum size
        self.setMinimumSize(100, 100)
        
        # Initialize angle (in degrees, 0-359)
        self._angle = 0.0
        self._pressed = False
        self._hover_angle = None  # Angle under mouse cursor when hovering
        
        # Additional configuration options
        self._origin_angle = 0.0  # Top is default origin/zero
        self._auto_return = False
        self._auto_return_threshold = 20.0  # Degrees from origin to auto-return
        self._min_angle = None  # No limits by default
        self._max_angle = None
        self._use_180_convention = False  # Use 0-359 by default
        self._show_cursor = True  # Show angle cursor
        
        # Important angles to highlight (beyond just the major angles)
        self._important_angles = []
        self._important_angles_labels = {}  # Maps angles to their labels
        self._highlight_important_angles = True
        
        # Drone status indicators
        self._show_drone_status = False
        self._drone_heading = None  # Current drone heading
        self._drone_target = None   # Target heading
        self._drone_home = None     # Home direction
        self._drone_wind = None     # Wind direction
        self._drone_status_colors = {
            'heading': QColor(0, 200, 255),    # Blue
            'target': QColor(50, 255, 50),     # Green
            'home': QColor(255, 150, 0),       # Orange
            'wind': QColor(255, 50, 50)        # Red
        }
        self._drone_status_thickness = {
            'heading': 3,
            'target': 2,
            'home': 2,
            'wind': 2
        }
        
        # Additional drone status indicators
        self._drone_velocity = None          # Current velocity vector direction
        self._drone_acceleration = None      # Current acceleration vector direction
        self._drone_gps_direction = None     # GPS direction to destination
        self._drone_obstacle = None          # Direction of nearest obstacle
        self._drone_custom_direction = None  # Custom direction indicator (configurable)
        
        # Additional status colors and thickness
        self._drone_status_colors.update({
            'velocity': QColor(100, 200, 255),     # Light blue
            'acceleration': QColor(100, 255, 200), # Light green
            'gps': QColor(255, 255, 100),          # Yellow
            'obstacle': QColor(255, 100, 100),     # Light red
            'custom': QColor(200, 100, 255)        # Purple
        })
        self._drone_status_thickness.update({
            'velocity': 2,
            'acceleration': 2,
            'gps': 2, 
            'obstacle': 2,
            'custom': 2
        })
        
        # Drone numeric status values (displayed as text)
        self._drone_altitude = None           # Current altitude in meters
        self._drone_ground_speed = None       # Ground speed in m/s
        self._drone_vertical_speed = None     # Vertical speed in m/s
        self._drone_battery_level = None      # Battery percentage
        self._drone_distance_to_home = None   # Distance to home in meters
        self._drone_custom_value = None       # Custom numeric value
        self._drone_custom_label = "Custom"   # Label for custom value
        
        # Display settings for numeric values
        self._show_numeric_values = True      # Whether to show numeric values
        self._numeric_precision = 1           # Decimal places for numeric values
        
        # Set focus policy to accept keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Enable mouse tracking for hover effects
        self.setMouseTracking(True)
    
    def sizeHint(self) -> QSize:
        """Suggest a default size for the widget.
        
        Returns:
            The suggested size
        """
        return QSize(150, 150)
        
    def paintEvent(self, event):
        """Draw the rotation dial widget.
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Calculate the dimensions
        width = self.width()
        height = self.height()
        size = min(width, height)
        center_x = width // 2
        center_y = height // 2
        radius = size // 2 - 10  # Smaller than the widget to allow for padding
        
        # Draw the outer circle
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        
        outer_rect = QRect(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.drawEllipse(outer_rect)
        
        # Draw orientation indicator line (shows current zero orientation)
        orientation_line_color = QColor(50, 200, 50, 100)
        painter.setPen(QPen(orientation_line_color, 1, Qt.DashLine))
        
        # Draw a line from center to the edge in the direction of the origin
        origin_rad = math.radians(self._origin_angle)
        origin_x = center_x + int(radius * 1.1 * math.sin(origin_rad))
        origin_y = center_y - int(radius * 1.1 * math.cos(origin_rad))
        painter.drawLine(center_x, center_y, origin_x, origin_y)
        
        # Draw degree markers
        painter.setPen(QPen(QColor(120, 120, 120), 1))
        for i in range(0, 360, 15):
            angle_rad = math.radians(i)
            
            # Calculate marker size based on whether it's a major or minor tick
            # and whether it aligns with the current orientation
            is_major = i % 90 == 0
            is_origin_aligned = (i % 90) == (int(self._origin_angle) % 90)
            
            # Make ticks that align with the current orientation more prominent
            tick_length = 5
            if is_major:
                tick_length = 10
            elif is_origin_aligned:
                tick_length = 8
                
            # Start position for the line
            inner_radius = radius - tick_length
            x1 = center_x + int(inner_radius * math.sin(angle_rad))
            y1 = center_y - int(inner_radius * math.cos(angle_rad))
            
            # End position for the line
            x2 = center_x + int(radius * math.sin(angle_rad))
            y2 = center_y - int(radius * math.cos(angle_rad))
            
            # Use different colors for ticks aligned with origin
            if is_origin_aligned and not is_major:
                painter.setPen(QPen(QColor(50, 180, 50), 1))
            else:
                painter.setPen(QPen(QColor(120, 120, 120), 1))
                
            painter.drawLine(x1, y1, x2, y2)
            
            # Draw degree numbers for major angles, adjusted for origin orientation
            if i % 90 == 0:
                text_radius = inner_radius - 15
                
                # Calculate text position with offset for better positioning
                text_width = 20  # Approximate width of the text
                text_height = 10  # Approximate height of the text
                
                # Adjust text position based on which quadrant it's in
                if i == 0:  # Top
                    x_offset = -text_width / 2
                    y_offset = -5
                elif i == 90:  # Right
                    x_offset = 5
                    y_offset = text_height / 2 - 5
                elif i == 180:  # Bottom
                    x_offset = -text_width / 2
                    y_offset = text_height + 5
                else:  # Left (270)
                    x_offset = -text_width - 5
                    y_offset = text_height / 2 - 5
                
                x_text = center_x + int(text_radius * math.sin(angle_rad)) + x_offset
                y_text = center_y - int(text_radius * math.cos(angle_rad)) + y_offset
                
                # Calculate display angle based on origin and convention
                display_angle = (i - self._origin_angle) % 360
                if self._use_180_convention and display_angle > 180:
                    display_angle = display_angle - 360
                
                # For major angles, show the display angle
                display_text = f"{int(display_angle)}°"
                
                painter.setPen(QColor(200, 200, 200))
                painter.drawText(int(x_text), int(y_text), display_text)
                
        # Draw min/max angle limits if set
        if self._min_angle is not None:
            min_rad = math.radians(self._min_angle)
            min_x = center_x + int(radius * 0.9 * math.sin(min_rad))
            min_y = center_y - int(radius * 0.9 * math.cos(min_rad))
            
            painter.setPen(QPen(QColor(200, 100, 50), 2))
            painter.setBrush(QBrush(QColor(200, 100, 50)))
            painter.drawRect(min_x - 3, min_y - 3, 6, 6)
            
            # Draw min label
            min_label_radius = radius * 0.9 + 10
            min_label_x = center_x + int(min_label_radius * math.sin(min_rad)) - 10
            min_label_y = center_y - int(min_label_radius * math.cos(min_rad)) + 5
            
            # Display min angle relative to origin if needed
            min_display = (self._min_angle - self._origin_angle) % 360
            if self._use_180_convention and min_display > 180:
                min_display = min_display - 360
                
            painter.setPen(QColor(200, 100, 50))
            painter.drawText(min_label_x, min_label_y, f"min")
        
        if self._max_angle is not None:
            max_rad = math.radians(self._max_angle)
            max_x = center_x + int(radius * 0.9 * math.sin(max_rad))
            max_y = center_y - int(radius * 0.9 * math.cos(max_rad))
            
            painter.setPen(QPen(QColor(200, 100, 50), 2))
            painter.setBrush(QBrush(QColor(200, 100, 50)))
            painter.drawRect(max_x - 3, max_y - 3, 6, 6)
            
            # Draw max label
            max_label_radius = radius * 0.9 + 10
            max_label_x = center_x + int(max_label_radius * math.sin(max_rad)) - 10
            max_label_y = center_y - int(max_label_radius * math.cos(max_rad)) + 5
            
            # Display max angle relative to origin if needed
            max_display = (self._max_angle - self._origin_angle) % 360
            if self._use_180_convention and max_display > 180:
                max_display = max_display - 360
                
            painter.setPen(QColor(200, 100, 50))
            painter.drawText(max_label_x, max_label_y, f"max")
        
        # Draw the current angle indicator (needle)
        angle_rad = math.radians(self._angle)
        needle_x = center_x + int(radius * 0.8 * math.sin(angle_rad))
        needle_y = center_y - int(radius * 0.8 * math.cos(angle_rad))
        
        painter.setPen(QPen(QColor(200, 50, 50), 2))
        painter.drawLine(center_x, center_y, needle_x, needle_y)
        
        # Draw indicator dot at the end of the needle
        painter.setBrush(QBrush(QColor(200, 50, 50)))
        painter.drawEllipse(QPoint(needle_x, needle_y), 5, 5)
        
        # Draw center dot
        painter.setBrush(QBrush(QColor(150, 150, 150)))
        painter.drawEllipse(QPoint(center_x, center_y), 3, 3)
        
        # Draw current angle text
        painter.setPen(QColor(200, 200, 200))
        font = QFont()
        font.setPointSize(10)
        painter.setFont(font)
        
        # Display the angle with 1 decimal place, adjusted for origin and convention
        display_angle = (self._angle - self._origin_angle) % 360
        if self._use_180_convention and display_angle > 180:
            display_angle = display_angle - 360
            
        angle_text = f"{display_angle:.1f}°"
        painter.drawText(center_x - 20, center_y + radius + 25, angle_text)
        
        # Draw cursor indicating current angle position if enabled
        if self._show_cursor and not self._pressed:
            cursor_rad = math.radians(self._angle)
            cursor_inner = radius + 5
            cursor_outer = radius + 12
            
            cursor_x1 = center_x + int(cursor_inner * math.sin(cursor_rad))
            cursor_y1 = center_y - int(cursor_inner * math.cos(cursor_rad))
            cursor_x2 = center_x + int(cursor_outer * math.sin(cursor_rad))
            cursor_y2 = center_y - int(cursor_outer * math.cos(cursor_rad))
            
            painter.setPen(QPen(QColor(220, 220, 100), 2))
            painter.drawLine(cursor_x1, cursor_y1, cursor_x2, cursor_y2)
        
        # Draw drone status indicators if enabled
        if self._show_drone_status:
            # Helper function to draw a status line
            def draw_status_line(angle, color, thickness):
                if angle is not None:
                    status_rad = math.radians(angle)
                    status_x = center_x + int(radius * 0.9 * math.sin(status_rad))
                    status_y = center_y - int(radius * 0.9 * math.cos(status_rad))
                    
                    painter.setPen(QPen(color, thickness))
                    painter.drawLine(center_x, center_y, status_x, status_y)
                    
                    # Draw indicator at the end of the line
                    painter.setBrush(QBrush(color))
                    painter.drawEllipse(QPoint(status_x, status_y), 3, 3)
            
            # Draw each status indicator
            draw_status_line(self._drone_heading, self._drone_status_colors['heading'], self._drone_status_thickness['heading'])
            draw_status_line(self._drone_target, self._drone_status_colors['target'], self._drone_status_thickness['target'])
            draw_status_line(self._drone_home, self._drone_status_colors['home'], self._drone_status_thickness['home'])
            draw_status_line(self._drone_wind, self._drone_status_colors['wind'], self._drone_status_thickness['wind'])
            draw_status_line(self._drone_velocity, self._drone_status_colors['velocity'], self._drone_status_thickness['velocity'])
            draw_status_line(self._drone_acceleration, self._drone_status_colors['acceleration'], self._drone_status_thickness['acceleration'])
            draw_status_line(self._drone_gps_direction, self._drone_status_colors['gps'], self._drone_status_thickness['gps'])
            draw_status_line(self._drone_obstacle, self._drone_status_colors['obstacle'], self._drone_status_thickness['obstacle'])
            draw_status_line(self._drone_custom_direction, self._drone_status_colors['custom'], self._drone_status_thickness['custom'])
            
            # Draw numeric status values if enabled
            if self._show_numeric_values:
                status_values = []
                
                # Format precision for all numeric values
                format_str = f"{{:.{self._numeric_precision}f}}"
                
                # Add each value with its label, if available
                if self._drone_altitude is not None:
                    status_values.append(f"Alt: {format_str.format(self._drone_altitude)}m")
                
                if self._drone_ground_speed is not None:
                    status_values.append(f"GS: {format_str.format(self._drone_ground_speed)}m/s")
                
                if self._drone_vertical_speed is not None:
                    status_values.append(f"VS: {format_str.format(self._drone_vertical_speed)}m/s")
                
                if self._drone_battery_level is not None:
                    status_values.append(f"Bat: {format_str.format(self._drone_battery_level)}%")
                
                if self._drone_distance_to_home is not None:
                    status_values.append(f"Home: {format_str.format(self._drone_distance_to_home)}m")
                
                if self._drone_custom_value is not None:
                    status_values.append(f"{self._drone_custom_label}: {format_str.format(self._drone_custom_value)}")
                
                # Draw status box if we have values to show
                if status_values:
                    # Create background for status values
                    status_box_height = len(status_values) * 15 + 10
                    status_box_width = 120
                    
                    status_box_x = width - status_box_width - 10
                    status_box_y = 10
                    
                    # Draw semi-transparent background
                    painter.setBrush(QBrush(QColor(30, 30, 30, 180)))
                    painter.setPen(QPen(QColor(100, 100, 100), 1))
                    painter.drawRoundedRect(status_box_x, status_box_y, status_box_width, status_box_height, 5, 5)
                    
                    # Draw status values
                    painter.setPen(QPen(QColor(220, 220, 220), 1))
                    for i, value in enumerate(status_values):
                        y_pos = status_box_y + 20 + (i * 15)
                        painter.drawText(status_box_x + 10, y_pos, value)
                        
                    # Draw "Drone Status" header
                    painter.setPen(QPen(QColor(150, 200, 255), 1))
                    painter.drawText(status_box_x + 10, status_box_y + 15, "Drone Status")
        
    def mousePressEvent(self, event):
        """Handle mouse press events.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._update_angle(event.x(), event.y())
            self.setFocus()
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events.
        
        Args:
            event: Mouse event
        """
        if self._pressed:
            self._update_angle(event.x(), event.y())
        else:
            # Calculate hover angle for visual feedback
            width = self.width()
            height = self.height()
            center_x = width // 2
            center_y = height // 2
            
            dx = event.x() - center_x
            dy = center_y - event.y()
            
            if dx != 0 or dy != 0:  # Avoid division by zero
                self._hover_angle = math.degrees(math.atan2(dx, dy)) % 360
                self.update()
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._pressed = False
            
            # Check if we should auto-return to origin
            if self._auto_return:
                self.set_angle(self._origin_angle)  # Return to origin immediately when released
    
    def leaveEvent(self, event):
        """Handle mouse leave events.
        
        Args:
            event: Leave event
        """
        self._hover_angle = None
        self.update()
    
    def keyPressEvent(self, event):
        """Handle keyboard events for rotation control.
        
        Allows control of the rotation with arrow keys.
        
        Args:
            event: Key event
        """
        step = 1.0  # Degrees to rotate per key press
        big_step = 15.0  # Larger step for Shift+arrow keys
        
        new_angle = self._angle
        
        if event.modifiers() & Qt.ShiftModifier:
            step = big_step
            
        if event.key() == Qt.Key_Left:
            new_angle = (self._angle - step) % 360
        elif event.key() == Qt.Key_Right:
            new_angle = (self._angle + step) % 360
        elif event.key() == Qt.Key_Up:
            # Move to the nearest multiple of 90 degrees
            new_angle = round(self._angle / 90) * 90 % 360
        elif event.key() == Qt.Key_Down:
            # Move to origin
            new_angle = self._origin_angle
        elif event.key() == Qt.Key_Home:
            # Return to origin
            new_angle = self._origin_angle
        elif event.key() == Qt.Key_End:
            # Go to opposite of origin
            new_angle = (self._origin_angle + 180) % 360
        else:
            super().keyPressEvent(event)
            return
            
        # Apply angle limits if set
        if self._min_angle is not None and self._max_angle is not None:
            # Handle wrapping cases for min/max angles
            min_angle = self._min_angle % 360
            max_angle = self._max_angle % 360
            
            if min_angle < max_angle:
                # Normal case: min is less than max
                if new_angle < min_angle or new_angle > max_angle:
                    # Clamp to nearest limit
                    if abs(new_angle - min_angle) < abs(new_angle - max_angle):
                        new_angle = min_angle
                    else:
                        new_angle = max_angle
            else:
                # Wrapped case: min is greater than max (e.g. min=330, max=30)
                if new_angle > max_angle and new_angle < min_angle:
                    # Clamp to nearest limit
                    if abs(new_angle - min_angle) < abs(new_angle - max_angle):
                        new_angle = min_angle
                    else:
                        new_angle = max_angle
        
        # Update angle if it changed
        if new_angle != self._angle:
            self._angle = new_angle
            self.update()
            self.angleChanged.emit(new_angle)
    
    def _update_angle(self, mouse_x, mouse_y):
        """Update rotation angle based on mouse coordinates.
        
        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position
        """
        # Calculate center
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        
        # Calculate the angle from center to mouse position
        dx = mouse_x - center_x
        dy = center_y - mouse_y  # Invert Y for logical coordinates
        
        if dx == 0 and dy == 0:
            return  # Avoid division by zero
            
        # Calculate angle in degrees (0 at top, clockwise)
        angle = math.degrees(math.atan2(dx, dy)) % 360
        
        # Apply angle limits if set
        if self._min_angle is not None and self._max_angle is not None:
            # Handle wrapping cases for min/max angles
            min_angle = self._min_angle % 360
            max_angle = self._max_angle % 360
            
            if min_angle < max_angle:
                # Normal case: min is less than max
                if angle < min_angle or angle > max_angle:
                    # Clamp to nearest limit
                    if abs(angle - min_angle) < abs(angle - max_angle):
                        angle = min_angle
                    else:
                        angle = max_angle
            else:
                # Wrapped case: min is greater than max (e.g. min=330, max=30)
                if angle > max_angle and angle < min_angle:
                    # Clamp to nearest limit
                    if abs(angle - min_angle) < abs(angle - max_angle):
                        angle = min_angle
                    else:
                        angle = max_angle
        
        # Update angle if changed
        if angle != self._angle:
            self._angle = angle
            self.update()
            self.angleChanged.emit(angle)
    
    def set_angle(self, angle):
        """Set the rotation angle programmatically.
        
        Args:
            angle: Angle in degrees
        """
        # Normalize angle to 0-359 range
        angle = angle % 360
        
        # Apply angle limits if set
        if self._min_angle is not None and self._max_angle is not None:
            # Handle wrapping cases for min/max angles
            min_angle = self._min_angle % 360
            max_angle = self._max_angle % 360
            
            if min_angle < max_angle:
                # Normal case: min is less than max
                if angle < min_angle or angle > max_angle:
                    # Clamp to nearest limit
                    if abs(angle - min_angle) < abs(angle - max_angle):
                        angle = min_angle
                    else:
                        angle = max_angle
            else:
                # Wrapped case: min is greater than max (e.g. min=330, max=30)
                if angle > max_angle and angle < min_angle:
                    # Clamp to nearest limit
                    if abs(angle - min_angle) < abs(angle - max_angle):
                        angle = min_angle
                    else:
                        angle = max_angle
        
        # Update if changed
        if angle != self._angle:
            self._angle = angle
            self.update()
            self.angleChanged.emit(angle)
    
    def get_angle(self):
        """Get the current rotation angle.
        
        Returns:
            The current angle in degrees (0-359)
        """
        return self._angle
    
    def get_display_angle(self):
        """Get the current display angle (adjusted for origin and convention).
        
        Returns:
            The display angle in degrees
        """
        display_angle = (self._angle - self._origin_angle) % 360
        if self._use_180_convention and display_angle > 180:
            display_angle = display_angle - 360
        return display_angle
    
    def set_origin_angle(self, angle):
        """Set the origin angle.
        
        Args:
            angle: Origin angle in degrees or a string name ('top', 'right', 'bottom', 'left')
        """
        if isinstance(angle, str):
            # Convert named orientations to angles
            orientation_map = {
                'top': 0.0,
                'right': 90.0,
                'bottom': 180.0,
                'left': 270.0
            }
            
            if angle.lower() in orientation_map:
                self._origin_angle = orientation_map[angle.lower()]
            else:
                # If not a recognized orientation name, default to top
                self._origin_angle = 0.0
        else:
            # Use the provided angle value
            self._origin_angle = angle % 360
            
        self.update()
    
    def set_auto_return(self, enabled, threshold=None):
        """Set auto-return to origin behavior.
        
        Args:
            enabled: Whether to enable auto-return
            threshold: Angle threshold for auto-return (in degrees)
        """
        self._auto_return = enabled
        if threshold is not None:
            self._auto_return_threshold = threshold
    
    def set_angle_limits(self, min_angle=None, max_angle=None):
        """Set the allowed angle range.
        
        Args:
            min_angle: Minimum allowed angle (or None for no limit)
            max_angle: Maximum allowed angle (or None for no limit)
        """
        self._min_angle = min_angle
        self._max_angle = max_angle
        
        # If current angle is outside limits, adjust it
        if min_angle is not None and max_angle is not None:
            self.set_angle(self._angle)  # This will apply the limits
    
    def set_angle_convention(self, use_180_convention):
        """Set the angle display convention.
        
        Args:
            use_180_convention: If True, use -180 to 180 range. If False, use 0 to 359.
        """
        self._use_180_convention = use_180_convention
        self.update()
    
    def set_cursor_visible(self, visible):
        """Set whether to show the angle cursor.
        
        Args:
            visible: Whether to show the cursor
        """
        self._show_cursor = visible
        self.update()
        
    def set_important_angles(self, angles, labels=None):
        """Set important angles to highlight on the dial.
        
        Args:
            angles: List of angles in degrees to highlight
            labels: Optional dictionary mapping angles to label strings
        """
        self._important_angles = [angle % 360 for angle in angles]
        
        if labels is not None:
            self._important_angles_labels = {angle % 360: label for angle, label in labels.items()}
        else:
            self._important_angles_labels = {}
            
        self.update()
        
    def set_highlight_important_angles(self, highlight):
        """Set whether to highlight important angles.
        
        Args:
            highlight: Whether to show special indicators for important angles
        """
        self._highlight_important_angles = highlight
        self.update()
        
    def get_important_angles(self):
        """Get the list of important angles.
        
        Returns:
            List of important angles in degrees
        """
        return self._important_angles.copy()
    
    def set_show_drone_status(self, show):
        """Enable or disable drone status indicators.
        
        Args:
            show: Whether to show drone status indicators
        """
        self._show_drone_status = show
        self.update()
        
    def set_drone_heading(self, heading):
        """Set the current drone heading.
        
        Args:
            heading: Current heading in degrees or None
        """
        if heading is not None:
            self._drone_heading = heading % 360
        else:
            self._drone_heading = None
        self.update()
        
    def set_drone_target(self, target):
        """Set the target heading.
        
        Args:
            target: Target heading in degrees or None
        """
        if target is not None:
            self._drone_target = target % 360
        else:
            self._drone_target = None
        self.update()
        
    def set_drone_home(self, home):
        """Set the home direction.
        
        Args:
            home: Home direction in degrees or None
        """
        if home is not None:
            self._drone_home = home % 360
        else:
            self._drone_home = None
        self.update()
        
    def set_drone_wind(self, wind):
        """Set the wind direction.
        
        Args:
            wind: Wind direction in degrees or None
        """
        if wind is not None:
            self._drone_wind = wind % 360
        else:
            self._drone_wind = None
        self.update()
        
    def set_drone_velocity(self, velocity):
        """Set the drone velocity vector direction.
        
        Args:
            velocity: Velocity vector direction in degrees or None
        """
        if velocity is not None:
            self._drone_velocity = velocity % 360
        else:
            self._drone_velocity = None
        self.update()
        
    def set_drone_acceleration(self, acceleration):
        """Set the drone acceleration vector direction.
        
        Args:
            acceleration: Acceleration vector direction in degrees or None
        """
        if acceleration is not None:
            self._drone_acceleration = acceleration % 360
        else:
            self._drone_acceleration = None
        self.update()
        
    def set_drone_gps_direction(self, gps):
        """Set the GPS direction to destination.
        
        Args:
            gps: GPS direction in degrees or None
        """
        if gps is not None:
            self._drone_gps_direction = gps % 360
        else:
            self._drone_gps_direction = None
        self.update()
        
    def set_drone_obstacle(self, obstacle):
        """Set the direction of nearest obstacle.
        
        Args:
            obstacle: Obstacle direction in degrees or None
        """
        if obstacle is not None:
            self._drone_obstacle = obstacle % 360
        else:
            self._drone_obstacle = None
        self.update()
        
    def set_drone_custom_direction(self, direction, label=None):
        """Set a custom direction indicator.
        
        Args:
            direction: Custom direction in degrees or None
            label: Optional label for this direction
        """
        if direction is not None:
            self._drone_custom_direction = direction % 360
        else:
            self._drone_custom_direction = None
            
        if label:
            self._drone_status_colors['custom'] = label
            
        self.update()
        
    def set_drone_altitude(self, altitude):
        """Set the drone altitude.
        
        Args:
            altitude: Altitude in meters or None
        """
        self._drone_altitude = altitude
        self.update()
        
    def set_drone_ground_speed(self, speed):
        """Set the drone ground speed.
        
        Args:
            speed: Ground speed in m/s or None
        """
        self._drone_ground_speed = speed
        self.update()
        
    def set_drone_vertical_speed(self, speed):
        """Set the drone vertical speed.
        
        Args:
            speed: Vertical speed in m/s or None
        """
        self._drone_vertical_speed = speed
        self.update()
        
    def set_drone_battery_level(self, level):
        """Set the drone battery level.
        
        Args:
            level: Battery percentage (0-100) or None
        """
        self._drone_battery_level = level
        self.update()
        
    def set_drone_distance_to_home(self, distance):
        """Set the distance to home.
        
        Args:
            distance: Distance in meters or None
        """
        self._drone_distance_to_home = distance
        self.update()
        
    def set_drone_custom_value(self, value, label=None):
        """Set a custom numeric value.
        
        Args:
            value: Custom numeric value or None
            label: Optional label for this value
        """
        self._drone_custom_value = value
        if label:
            self._drone_custom_label = label
        self.update()
        
    def set_show_numeric_values(self, show):
        """Set whether to show numeric status values.
        
        Args:
            show: Whether to show numeric values
        """
        self._show_numeric_values = show
        self.update()
        
    def set_numeric_precision(self, precision):
        """Set decimal precision for numeric values.
        
        Args:
            precision: Number of decimal places (0-5)
        """
        self._numeric_precision = max(0, min(5, precision))
        self.update()
        

class RotationParameter(Parameter):
    """Rotation parameter for controlling angle values.
    
    A parameter widget providing a circular control for selecting angles.
    The angle is measured in degrees from 0 to 359.
    
    Attributes:
        name (str): Display name of the parameter
        value (float): Current parameter value in degrees
        rotation_dial (RotationDialWidget): The rotation dial control widget
    """
    
    def __init__(self, name: str = "Unnamed", config: Optional[Dict] = None) -> None:
        """Initialize the rotation parameter widget.
        
        Args:
            name: Display name of the parameter
            config: Configuration dictionary with optional keys:
                - initial: Initial angle in degrees (default: 0.0)
                - size: Widget size in pixels (default: uses sizeHint)
                - snap: Whether to snap to nearest degree (default: False)
                - snap_angles: List of angles to snap to (default: [0, 90, 180, 270])
                - snap_threshold: Angle threshold for snapping in degrees (default: 5.0)
                - zero_orientation: Orientation of zero angle ('top', 'right', 'bottom', 'left', or degrees)
                - use_180_convention: Whether to use -180 to 180 range instead of 0-359 (default: False)
                - auto_return: Whether to return to origin when released (default: False)
                - min_angle: Minimum allowed angle in degrees (default: None - no limit)
                - max_angle: Maximum allowed angle in degrees (default: None - no limit)
                - show_cursor: Whether to show the angle cursor (default: True)
                - show_drone_status: Whether to show drone status indicators (default: False)
                - important_angles: List of angles to highlight (default: [])
                - important_angle_labels: Dictionary mapping angles to label strings
        """
        super().__init__(name, config)
        config = config or {}
    
    def setup_ui(self):
        """Set up the UI components for the rotation parameter."""
        # Create layout for rotation dial (center aligned)
        dial_layout = QVBoxLayout()
        dial_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create the rotation dial widget
        self.rotation_dial = RotationDialWidget()
        
        # Set custom size if provided
        if 'size' in self.config:
            size = self.config['size']
            self.rotation_dial.setFixedSize(size, size)
            
        # Snapping options
        self.snap_enabled = self.config.get('snap', False)
        self.snap_angles = self.config.get('snap_angles', [0, 90, 180, 270])
        self.snap_threshold = self.config.get('snap_threshold', 5.0)
        
        # Set zero orientation
        if 'zero_orientation' in self.config:
            self.rotation_dial.set_origin_angle(self.config['zero_orientation'])
        
        # Set angle convention
        if 'use_180_convention' in self.config:
            self.rotation_dial.set_angle_convention(self.config['use_180_convention'])
        
        # Set auto-return behavior
        if 'auto_return' in self.config:
            self.rotation_dial.set_auto_return(self.config['auto_return'])
        
        # Set angle limits
        min_angle = self.config.get('min_angle', None)
        max_angle = self.config.get('max_angle', None)
        if min_angle is not None and max_angle is not None:
            self.rotation_dial.set_angle_limits(min_angle, max_angle)
            
        # Set initial angle
        initial_angle = self.config.get('initial', 0.0)
        self.value = initial_angle % 360  # Normalize to 0-359
        self.rotation_dial.set_angle(self.value)
        
        # Connect signals
        self.rotation_dial.angleChanged.connect(self._on_angle_changed)
        
        # Add rotation dial to layout
        dial_layout.addWidget(self.rotation_dial)
        
        # Add to working layout
        self.working_layout.addLayout(dial_layout)
    
    def _on_angle_changed(self, angle):
        """Handle angle changes from the rotation dial widget.
        
        Args:
            angle: Angle in degrees (0-359)
        """
        # Apply snapping if enabled
        if self.snap_enabled:
            # Find the closest snap angle
            closest_angle = min(self.snap_angles, 
                               key=lambda snap_angle: min(
                                   abs(angle - snap_angle),
                                   abs(angle - snap_angle - 360),
                                   abs(angle - snap_angle + 360)
                               ))
            
            # Check if within threshold
            min_diff = min(
                abs(angle - closest_angle),
                abs(angle - closest_angle - 360),
                abs(angle - closest_angle + 360)
            )
            
            if min_diff <= self.snap_threshold:
                angle = closest_angle
                self.rotation_dial.set_angle(angle)
        
        self.value = angle
        self.valueChanged.emit(self.name, self.value)
    
    def set_value(self, value, trigger_callback=True):
        """Set the parameter value programmatically.
        
        Args:
            value: The new angle in degrees
            trigger_callback: Whether to emit the valueChanged signal
        """
        angle = float(value) % 360  # Normalize to 0-359
        self.value = angle
        self.rotation_dial.set_angle(angle)
        
        if trigger_callback:
            self.valueChanged.emit(self.name, self.value)
    
    def get_value(self):
        """Get the current parameter value.
        
        Returns:
            The current angle in degrees (0-359)
        """
        return self.rotation_dial.get_display_angle()
    
    def get_display_angle(self):
        """Get the display angle (adjusted for origin and convention).
        
        Returns:
            The display angle in degrees
        """
        return self.rotation_dial.get_display_angle()

    def register_callback(self, callback):
        """Register a callback function for value changes.
        
        Args:
            callback: Function to call when the value changes
        """
        self.valueChanged.connect(callback)