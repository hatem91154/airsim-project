"""Joystick parameter for PyQt Live Tuner.

This module provides the JoystickParameter class, which implements a 2D joystick
control widget for tuning x,y coordinate parameters simultaneously.
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QPoint, QRect, QSize, pyqtSignal, QTimer
from typing import Callable, Dict, Optional, Tuple, Any, Union
from math import sqrt, pow


from .parameter import Parameter

# Return mode constants for configuration
RETURN_MODE_NONE = "none"
RETURN_MODE_HORIZONTAL = "horizontal"
RETURN_MODE_VERTICAL = "vertical"
RETURN_MODE_BOTH = "both"


class JoystickWidget(QWidget):
    """Custom widget that implements the joystick control UI.
    
    A square widget that tracks mouse movements to simulate a 2D joystick.
    The position is normalized to range from -1.0 to 1.0 in both axes.
    
    Attributes:
        positionChanged: Signal emitted when position changes (x, y)
        _position: Current joystick position as (x, y) tuple
        _handle_radius: Radius of the joystick handle in pixels
        _pressed: Whether the joystick is currently being pressed/dragged
        _return_mode: Mode that controls auto-return behavior when released
        _dead_zone: Dead zone value (0.0 to 1.0) to reduce sensitivity
        _dead_zone_x: X-axis specific dead zone value
        _dead_zone_y: Y-axis specific dead zone value
        _exponential_x: X-axis exponential response factor (1.0 = linear)
        _exponential_y: Y-axis exponential response factor (1.0 = linear)
        _update_timer: Timer for periodic position updates when pressed
        _update_frequency: Update frequency in Hz
        _is_in_dead_zone: Whether the current position is inside the dead zone
    """
    
    positionChanged = pyqtSignal(float, float)
    
    def __init__(self, parent=None):
        """Initialize the joystick widget."""
        super().__init__(parent)
        
        # Set minimum size
        self.setMinimumSize(100, 100)
        
        # Initialize position (x, y in range -1.0 to 1.0)
        self._position = (0.0, 0.0)
        self._raw_position = (0.0, 0.0)  # Position before dead zone is applied
        self._handle_radius = 10
        self._pressed = False
        
        # Return to center behavior
        self._return_mode = RETURN_MODE_BOTH
        
        # Dead zone settings
        self._dead_zone = 0.0      # Radial dead zone (circular)
        self._dead_zone_x = 0.0    # X-axis specific dead zone
        self._dead_zone_y = 0.0    # Y-axis specific dead zone
        
        # Exponential response settings
        self._exponential_x = 1.0  # X-axis exponential factor (internal, 1.0 = linear)
        self._exponential_y = 1.0  # Y-axis exponential factor (internal, 1.0 = linear)
        self._exponential_x_percent = 0.0  # X-axis exponential percentage (0-100%)
        self._exponential_y_percent = 0.0  # Y-axis exponential percentage (0-100%)
        
        # Track whether we're in any dead zone
        self._is_in_dead_zone = False
        self._is_in_x_dead_zone = False
        self._is_in_y_dead_zone = False
        
        # Update timer for continuous updates when pressed
        self._update_timer = QTimer(self)
        self._update_timer.timeout.connect(self._emit_position)
        self._update_frequency = 10  # Default: 10 Hz
        self._update_interval = 1000 // self._update_frequency  # Convert to ms
        
        # Set focus policy to accept keyboard focus
        self.setFocusPolicy(Qt.StrongFocus)
    
    def _emit_position(self):
        """Emit the current position through the signal."""
        if self._pressed and not self._is_in_dead_zone:
            self.positionChanged.emit(*self._position)
    
    def set_update_frequency(self, frequency_hz: float):
        """Set the update frequency for continuous updates when pressed.
        
        Args:
            frequency_hz: Frequency in Hz (updates per second)
        """
        if frequency_hz > 0:
            self._update_frequency = frequency_hz
            # Convert to millisecond interval (rounded to nearest ms)
            self._update_interval = round(1000 / frequency_hz)
            
            # Restart timer if it's running
            if self._update_timer.isActive():
                self._update_timer.stop()
                self._update_timer.start(self._update_interval)
                
    def get_update_frequency(self) -> float:
        """Get the current update frequency.
        
        Returns:
            The update frequency in Hz
        """
        return self._update_frequency
        
    def set_dead_zone(self, dead_zone: float):
        """Set the radial dead zone for the joystick.
        
        The dead zone is a radius around the center (0,0) where input is ignored.
        Values are clamped to the range 0.0 to 0.9.
        
        Args:
            dead_zone: Dead zone value (0.0 to 1.0)
        """
        # Clamp to valid range (0.0 to 0.9)
        self._dead_zone = max(0.0, min(0.9, dead_zone))
        
        # Check if current position is in the dead zone
        self._check_dead_zone(*self._raw_position)
        
    def set_axis_dead_zones(self, x_dead_zone: float, y_dead_zone: float):
        """Set separate dead zones for X and Y axes.
        
        Args:
            x_dead_zone: X-axis dead zone (0.0 to 0.9)
            y_dead_zone: Y-axis dead zone (0.0 to 0.9)
        """
        self._dead_zone_x = max(0.0, min(0.9, x_dead_zone))
        self._dead_zone_y = max(0.0, min(0.9, y_dead_zone))
        
        # Check if current position is in any dead zone
        self._check_dead_zone(*self._raw_position)

    def _check_dead_zone(self, x: float, y: float) -> bool:
        """Check if the given position is within any dead zone.
        
        Args:
            x: X position (-1.0 to 1.0)
            y: Y position (-1.0 to 1.0)
            
        Returns:
            True if position is in any dead zone, False otherwise
        """
        # Store raw position
        self._raw_position = (x, y)
        
        # Check circular dead zone
        distance = sqrt(x*x + y*y)
        in_circular_dead_zone = distance < self._dead_zone
        
        # Check axis-specific dead zones
        self._is_in_x_dead_zone = abs(x) < self._dead_zone_x
        self._is_in_y_dead_zone = abs(y) < self._dead_zone_y
        
        # The position is in a dead zone if it's in the circular dead zone
        # or if it's in both axis-specific dead zones
        self._is_in_dead_zone = in_circular_dead_zone or (self._is_in_x_dead_zone and self._is_in_y_dead_zone)
        
        return self._is_in_dead_zone

    def set_exponential(self, x_expo_percent: float, y_expo_percent: float):
        """Set exponential response factors for X and Y axes.
        
        Args:
            x_expo_percent: X-axis exponential percentage (0% = linear, 100% = max exponential)
            y_expo_percent: Y-axis exponential percentage (0% = linear, 100% = max exponential)
            
        Typical Expo Range:
            0%: Pure linear, sharp, and immediate response
            10-30%: Mild smoothing — good for basic acro/racing
            30-60%: Moderate smoothing — good for cinematic shots or beginner flying
            60-90%: High smoothing — best for ultra-precise or safe flying
            100%: Maximum smoothing — generally only used for special cases
        """
        # Clamp percentage to 0-100% range
        x_expo_percent = max(0.0, min(100.0, x_expo_percent))
        y_expo_percent = max(0.0, min(100.0, y_expo_percent))
        
        # Convert percentage to internal exponential factor (1.0 = linear, 5.0 = max exponential)
        # Using a maximum factor of 5.0 which provides a good range of control
        MAX_EXPO_FACTOR = 5.0
        
        # Calculate the exponential factor from percentage (0% -> 1.0, 100% -> MAX_EXPO_FACTOR)
        self._exponential_x = 1.0 + (MAX_EXPO_FACTOR - 1.0) * (x_expo_percent / 100.0)
        self._exponential_y = 1.0 + (MAX_EXPO_FACTOR - 1.0) * (y_expo_percent / 100.0)
        
        # Store the percentage values for display and config
        self._exponential_x_percent = x_expo_percent
        self._exponential_y_percent = y_expo_percent
        
        # Update the current position with the new exponential factors
        if self._raw_position != (0.0, 0.0):
            x, y = self._apply_dead_zone(*self._raw_position)
            self._position = self._apply_exponential(x, y)
            self.update()

    def _apply_exponential(self, x: float, y: float) -> Tuple[float, float]:
        """Apply exponential response to a position.
        
        Args:
            x: X position (-1.0 to 1.0)
            y: Y position (-1.0 to 1.0)
            
        Returns:
            Position with exponential response applied (x, y)
        """
        # If exponential factors are 1.0 (0% expo), no change needed
        if self._exponential_x_percent == 0.0 and self._exponential_y_percent == 0.0:
            return (x, y)
            
        # Apply exponential response to each axis while preserving sign
        result_x = x
        result_y = y
        
        # Use the standard expo formula: output = input * (1 - expo) + (input^3) * expo
        # This creates a smooth blend between linear and cubic response
        
        if self._exponential_x_percent > 0.0 and x != 0.0:
            # Convert percentage (0-100%) to normalized expo factor (0-1)
            expo_factor = self._exponential_x_percent / 100.0
            # Apply the formula while preserving sign
            sign_x = 1.0 if x > 0.0 else -1.0
            abs_x = abs(x)
            # Standard expo formula: linear blend with cubic
            result_x = sign_x * (abs_x * (1.0 - expo_factor) + (abs_x ** 3) * expo_factor)
            
        if self._exponential_y_percent > 0.0 and y != 0.0:
            # Convert percentage (0-100%) to normalized expo factor (0-1)
            expo_factor = self._exponential_y_percent / 100.0
            # Apply the formula while preserving sign
            sign_y = 1.0 if y > 0.0 else -1.0
            abs_y = abs(y)
            # Standard expo formula: linear blend with cubic
            result_y = sign_y * (abs_y * (1.0 - expo_factor) + (abs_y ** 3) * expo_factor)
            
        return (result_x, result_y)

    def _apply_dead_zone(self, x: float, y: float) -> Tuple[float, float]:
        """Apply dead zones to raw position values.
        
        This method implements axis-specific dead zones in addition to the circular dead zone.
        For axis dead zones, when one axis is in its dead zone but the other isn't,
        the axis in the dead zone is zeroed out.
        
        Args:
            x: Raw X position (-1.0 to 1.0)
            y: Raw Y position (-1.0 to 1.0)
            
        Returns:
            Position with dead zone applied (x, y)
        """
        # Check all dead zones first
        self._check_dead_zone(x, y)
        
        # Calculate distance from center for circular dead zone
        distance = sqrt(x*x + y*y)
        
        # Apply circular dead zone - if within circular dead zone, return (0,0)
        if distance < self._dead_zone:
            return (0.0, 0.0)
            
        # Apply axis-specific dead zones - if one axis is in dead zone but other isn't,
        # zero out the axis in the dead zone
        result_x = x
        result_y = y
        
        # If we're in X axis dead zone but not in circular dead zone, zero out X
        if self._is_in_x_dead_zone and not distance < self._dead_zone:
            result_x = 0.0
            
        # If we're in Y axis dead zone but not in circular dead zone, zero out Y    
        if self._is_in_y_dead_zone and not distance < self._dead_zone:
            result_y = 0.0
            
        return (result_x, result_y)
    
    def sizeHint(self) -> QSize:
        """Suggest a default size for the widget.
        
        Returns:
            The suggested size
        """
        return QSize(150, 150)
        
    def paintEvent(self, event):
        """Draw the joystick widget.
        
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
        radius = size // 2
        
        # Draw the outer border (circle)
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        
        outer_rect = QRect((width - size) // 2, (height - size) // 2, size, size)
        painter.drawEllipse(outer_rect)
        
        # Draw exponential response visualization if enabled
        if self._exponential_x > 1.0 or self._exponential_y > 1.0:
            self._draw_exponential_visualization(painter, center_x, center_y, radius)
        
        # Draw the circular dead zone if it's set
        if self._dead_zone > 0.0:
            # Calculate the dead zone radius
            dead_zone_radius = int(radius * self._dead_zone)
            
            # Create a semi-transparent red for the dead zone
            dead_zone_color = QColor(255, 0, 0, 40)  # Red with 40/255 alpha (translucent)
            painter.setPen(QPen(QColor(255, 0, 0, 100), 1))  # Slightly more opaque red for the border
            painter.setBrush(QBrush(dead_zone_color))
            
            # Draw the dead zone circle
            dead_zone_rect = QRect(
                center_x - dead_zone_radius, 
                center_y - dead_zone_radius,
                dead_zone_radius * 2,
                dead_zone_radius * 2
            )
            painter.drawEllipse(dead_zone_rect)
            
        # Draw X-axis dead zone if set
        if self._dead_zone_x > 0.0:
            # Calculate the dead zone width
            x_dead_zone_width = int(radius * self._dead_zone_x)
            
            # Create a semi-transparent yellow for the X dead zone
            x_dead_zone_color = QColor(255, 255, 0, 30)  # Yellow with 30/255 alpha
            painter.setPen(QPen(QColor(255, 255, 0, 80), 1))  # More opaque yellow for border
            painter.setBrush(QBrush(x_dead_zone_color))
            
            # Draw the X-axis dead zone rectangle
            x_dead_zone_rect = QRect(
                center_x - x_dead_zone_width,
                center_y - radius + 5,
                x_dead_zone_width * 2,
                2 * radius - 10
            )
            painter.drawRect(x_dead_zone_rect)
            
        # Draw Y-axis dead zone if set
        if self._dead_zone_y > 0.0:
            # Calculate the dead zone height
            y_dead_zone_height = int(radius * self._dead_zone_y)
            
            # Create a semi-transparent green for the Y dead zone
            y_dead_zone_color = QColor(0, 255, 0, 30)  # Green with 30/255 alpha
            painter.setPen(QPen(QColor(0, 255, 0, 80), 1))  # More opaque green for border
            painter.setBrush(QBrush(y_dead_zone_color))
            
            # Draw the Y-axis dead zone rectangle
            y_dead_zone_rect = QRect(
                center_x - radius + 5,
                center_y - y_dead_zone_height,
                2 * radius - 10,
                y_dead_zone_height * 2
            )
            painter.drawRect(y_dead_zone_rect)

        # Draw X and Y axes
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        # X-axis (horizontal line)
        painter.drawLine(center_x - radius + 5, center_y, center_x + radius - 5, center_y)
        # Y-axis (vertical line)
        painter.drawLine(center_x, center_y - radius + 5, center_x, center_y + radius - 5)
        
        # Draw the center position marker
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        
        # Draw crosshair at center
        painter.drawLine(center_x - 5, center_y, center_x + 5, center_y)
        painter.drawLine(center_x, center_y - 5, center_x, center_y + 5)
        
        # Calculate the handle position
        x, y = self._position
        handle_x = center_x + int(x * (size // 2 - self._handle_radius))
        handle_y = center_y - int(y * (size // 2 - self._handle_radius))  # Invert Y for screen coords
        
        # Set handle color based on whether it's in a dead zone
        if self._is_in_dead_zone:
            handle_color = QColor(200, 100, 100)  # Reddish when in dead zone
        elif self._is_in_x_dead_zone:
            handle_color = QColor(200, 200, 100)  # Yellowish when in X dead zone
        elif self._is_in_y_dead_zone:
            handle_color = QColor(100, 200, 100)  # Greenish when in Y dead zone
        else:
            handle_color = QColor(100, 150, 255)  # Bluish when outside all dead zones
        
        # Draw the handle
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(handle_color))
        painter.drawEllipse(QPoint(handle_x, handle_y), self._handle_radius, self._handle_radius)
        
        # Draw connection line from center to handle
        painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.DashLine))
        painter.drawLine(center_x, center_y, handle_x, handle_y)
        
        # Display current coordinates near the handle
        painter.setPen(QColor(255, 255, 255))
        coord_text = f"({x:.2f}, {y:.2f})"
        
        # Add indicator for current state
        if self._is_in_dead_zone:
            coord_text += " [DEAD ZONE]"
        elif self._is_in_x_dead_zone:
            coord_text += " [X DEAD]"
        elif self._is_in_y_dead_zone:
            coord_text += " [Y DEAD]"
        elif self._exponential_x > 1.0 or self._exponential_y > 1.0:
            # Show percentage values instead of raw factors
            x_percent = self._exponential_x_percent
            y_percent = self._exponential_y_percent
            coord_text += f" [EXP {x_percent:.0f}%,{y_percent:.0f}%]"
            
        painter.drawText(handle_x + 15, handle_y, coord_text)
    
    def _draw_exponential_visualization(self, painter, center_x, center_y, radius):
        """Draw visualization of exponential response curve.
        
        Args:
            painter: QPainter instance
            center_x: X center of the joystick
            center_y: Y center of the joystick
            radius: Radius of the joystick area
        """
        # Save current painter state
        painter.save()
        
        # Use smaller radius for curves to ensure they stay within the circle
        curve_radius = int(radius * 0.85)
        
        # Use semi-transparent colors for better visibility
        x_curve_color = QColor(255, 80, 80, 180)  # Red with some transparency
        y_curve_color = QColor(80, 80, 255, 180)  # Blue with some transparency
        
        # Create a clipping path to limit drawing to inside the circle
        clip_path = QPainterPath()
        clip_path.addEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.setClipPath(clip_path)
        
        # Draw X-axis exponential grid if enabled
        if self._exponential_x_percent > 0.0:
            # Set pen to a solid red line for the curve
            painter.setPen(QPen(x_curve_color, 2, Qt.SolidLine))
            
            # Create a path for the exponential curve using the standard expo formula
            path = QPainterPath()
            
            # Draw X-axis curve
            points = []
            expo_factor = self._exponential_x_percent / 100.0  # Convert to 0-1 range
            
            # Add many points to make the curve smooth
            for i in range(101):
                # Input from -1.0 to 1.0
                input_x = -1.0 + (i * 0.02)
                
                # Calculate output using the standard expo formula
                sign_x = 1.0 if input_x > 0.0 else -1.0
                abs_x = abs(input_x)
                # Standard expo formula: linear blend with cubic
                output_x = sign_x * (abs_x * (1.0 - expo_factor) + (abs_x ** 3) * expo_factor)
                
                # Calculate pixel positions (using smaller curve_radius to avoid edge overlap)
                px = center_x + int(input_x * curve_radius)  # X position based on input
                py = center_y - int(output_x * curve_radius)  # Y position based on output (inverted)
                
                points.append((px, py))
            
            # Create the path
            if points:
                path.moveTo(points[0][0], points[0][1])
                for px, py in points[1:]:
                    path.lineTo(px, py)
                    
            painter.drawPath(path)
            
            # Draw small label to indicate X-axis expo (moved inside for better positioning)
            painter.setPen(QPen(x_curve_color, 1))
            # Position label closer to the center to ensure it stays inside the circle
            label_x = center_x + int(curve_radius * 0.5)
            label_y = center_y - int(curve_radius * 0.5)
            painter.drawText(label_x, label_y, f"X:{self._exponential_x_percent:.0f}%")
            
        # Draw Y-axis exponential grid if enabled
        if self._exponential_y_percent > 0.0:
            # Set pen to a solid blue line for the curve (to distinguish from X)
            painter.setPen(QPen(y_curve_color, 2, Qt.SolidLine))
            
            # Create a path for the exponential curve using the standard expo formula
            path = QPainterPath()
            
            # Draw Y-axis curve
            points = []
            expo_factor = self._exponential_y_percent / 100.0  # Convert to 0-1 range
            
            # Add many points to make the curve smooth
            for i in range(101):
                # Input from -1.0 to 1.0
                input_y = -1.0 + (i * 0.02)
                
                # Calculate output using the standard expo formula
                sign_y = 1.0 if input_y > 0.0 else -1.0
                abs_y = abs(input_y)
                # Standard expo formula: linear blend with cubic
                output_y = sign_y * (abs_y * (1.0 - expo_factor) + (abs_y ** 3) * expo_factor)
                
                # Calculate pixel positions (using smaller curve_radius to avoid edge overlap)
                px = center_x + int(output_y * curve_radius)  # X position based on output
                py = center_y - int(input_y * curve_radius)  # Y position based on input (inverted)
                
                points.append((px, py))
            
            # Create the path
            if points:
                path.moveTo(points[0][0], points[0][1])
                for px, py in points[1:]:
                    path.lineTo(px, py)
                    
            painter.drawPath(path)
            
            # Draw small label to indicate Y-axis expo (moved inside for better positioning)
            painter.setPen(QPen(y_curve_color, 1))
            # Position label closer to the center to ensure it stays inside the circle
            label_x = center_x - int(curve_radius * 0.3)
            label_y = center_y - int(curve_radius * 0.5)
            painter.drawText(label_x, label_y, f"Y:{self._exponential_y_percent:.0f}%")
            
        # Draw 1:1 reference line (diagonal) with a dotted light gray line
        if self._exponential_x_percent > 0.0 or self._exponential_y_percent > 0.0:
            painter.setPen(QPen(QColor(150, 150, 150, 80), 1, Qt.DotLine))
            painter.drawLine(center_x - curve_radius, center_y + curve_radius, 
                            center_x + curve_radius, center_y - curve_radius)
        
        # Restore painter state (which also removes the clipping path)
        painter.restore()
    
    def mousePressEvent(self, event):
        """Handle mouse press events.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._pressed = True
            self._update_position(event.x(), event.y(), emit_signal=False)
            self.setFocus()
            # Emit initial position immediately only if outside dead zone
            if not self._is_in_dead_zone:
                self.positionChanged.emit(*self._position)
            # Start the update timer with current frequency
            self._update_timer.start(self._update_interval)
    
    def mouseMoveEvent(self, event):
        """Handle mouse move events.
        
        Args:
            event: Mouse event
        """
        if self._pressed:
            prev_in_dead_zone = self._is_in_dead_zone
            self._update_position(event.x(), event.y(), emit_signal=False)
            
            # If we've moved from inside to outside the dead zone, emit the position
            if prev_in_dead_zone and not self._is_in_dead_zone:
                self.positionChanged.emit(*self._position)
    
    def mouseReleaseEvent(self, event):
        """Handle mouse release events.
        
        Args:
            event: Mouse event
        """
        if event.button() == Qt.LeftButton:
            self._pressed = False
            # Stop the update timer
            self._update_timer.stop()
            self._apply_return_to_center(emit_signal=True)
    
    def _apply_return_to_center(self, emit_signal=True):
        """Apply the return-to-center behavior based on the configured return mode.
        
        Args:
            emit_signal: Whether to emit positionChanged signal
        """
        x, y = self._position
        
        # Apply return to center based on mode
        if self._return_mode == RETURN_MODE_BOTH:
            x, y = 0.0, 0.0
        elif self._return_mode == RETURN_MODE_HORIZONTAL:
            x = 0.0
        elif self._return_mode == RETURN_MODE_VERTICAL:
            y = 0.0
        # RETURN_MODE_NONE: Do nothing, stick stays where it is
        
        # Update position if changed
        if (x, y) != self._position:
            self._position = (x, y)
            self.update()
            if emit_signal:
                self.positionChanged.emit(x, y)
    
    def set_return_mode(self, mode: str):
        """Set the return-to-center mode.
        
        Args:
            mode: One of the RETURN_MODE_* constants
        """
        if mode in (RETURN_MODE_NONE, RETURN_MODE_HORIZONTAL, RETURN_MODE_VERTICAL, RETURN_MODE_BOTH):
            self._return_mode = mode
    
    def keyPressEvent(self, event):
        """Handle keyboard events for joystick control.
        
        Args:
            event: Key event
        """
        x, y = self._position
        step = 0.1
        
        if event.key() == Qt.Key_Left:
            x = max(-1.0, x - step)
        elif event.key() == Qt.Key_Right:
            x = min(1.0, x + step)
        elif event.key() == Qt.Key_Up:
            y = min(1.0, y + step)
        elif event.key() == Qt.Key_Down:
            y = max(-1.0, y - step)
        elif event.key() == Qt.Key_Space:
            # Reset to center
            x, y = 0.0, 0.0
        else:
            super().keyPressEvent(event)
            return
            
        # Update position if it changed
        if (x, y) != self._position:
            self._position = (x, y)
            self.update()
            self.positionChanged.emit(x, y)
    
    def _update_position(self, mouse_x, mouse_y, emit_signal=False):
        """Update joystick position based on mouse coordinates.
        
        Converts screen coordinates to normalized -1.0 to 1.0 range.
        
        Args:
            mouse_x: Mouse X position
            mouse_y: Mouse Y position
            emit_signal: Whether to emit positionChanged signal
        """
        # Calculate center and radius
        width = self.width()
        height = self.height()
        center_x = width // 2
        center_y = height // 2
        max_distance = min(width, height) // 2 - self._handle_radius
        
        # Calculate the distance from center
        dx = mouse_x - center_x
        dy = center_y - mouse_y  # Invert Y for logical coordinates
        
        # Calculate the distance and angle
        from math import sqrt
        distance = sqrt(dx*dx + dy*dy)
        
        # Normalize the position to -1.0 to 1.0 range
        if distance > max_distance:
            dx = dx * max_distance / distance
            dy = dy * max_distance / distance
            distance = max_distance
        
        # Convert to normalized coordinates
        raw_x = dx / max_distance if max_distance > 0 else 0
        raw_y = dy / max_distance if max_distance > 0 else 0
        
        # Apply dead zones
        x, y = self._apply_dead_zone(raw_x, raw_y)
        
        # Apply exponential response
        x, y = self._apply_exponential(x, y)
        
        # Update position if changed
        if (x, y) != self._position:
            self._position = (x, y)
            self.update()
            # Only emit signal if requested and not in dead zone
            if emit_signal and not self._is_in_dead_zone:
                self.positionChanged.emit(x, y)
    
    def set_position(self, x: float, y: float):
        """Set the joystick position programmatically.
        
        Args:
            x: X position (-1.0 to 1.0)
            y: Y position (-1.0 to 1.0)
        """
        # Clamp values to valid range
        x = max(-1.0, min(1.0, x))
        y = max(-1.0, min(1.0, y))
        
        # Store as raw position
        self._raw_position = (x, y)
        
        # Apply dead zone
        x, y = self._apply_dead_zone(x, y)
        
        # Apply exponential
        x, y = self._apply_exponential(x, y)
        
        # Update if changed
        if (x, y) != self._position:
            self._position = (x, y)
            self.update()
            if not self._is_in_dead_zone:
                self.positionChanged.emit(x, y)
    
    def paintEvent(self, event):
        """Draw the joystick widget.
        
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
        radius = size // 2
        
        # Draw the outer border (circle)
        painter.setPen(QPen(QColor(100, 100, 100), 2))
        painter.setBrush(QBrush(QColor(50, 50, 50)))
        
        outer_rect = QRect((width - size) // 2, (height - size) // 2, size, size)
        painter.drawEllipse(outer_rect)
        
        # Draw exponential response visualization if enabled
        if self._exponential_x > 1.0 or self._exponential_y > 1.0:
            self._draw_exponential_visualization(painter, center_x, center_y, radius)
        
        # Draw the circular dead zone if it's set
        if self._dead_zone > 0.0:
            # Calculate the dead zone radius
            dead_zone_radius = int(radius * self._dead_zone)
            
            # Create a semi-transparent red for the dead zone
            dead_zone_color = QColor(255, 0, 0, 40)  # Red with 40/255 alpha (translucent)
            painter.setPen(QPen(QColor(255, 0, 0, 100), 1))  # Slightly more opaque red for the border
            painter.setBrush(QBrush(dead_zone_color))
            
            # Draw the dead zone circle
            dead_zone_rect = QRect(
                center_x - dead_zone_radius, 
                center_y - dead_zone_radius,
                dead_zone_radius * 2,
                dead_zone_radius * 2
            )
            painter.drawEllipse(dead_zone_rect)
            
        # Draw X-axis dead zone if set
        if self._dead_zone_x > 0.0:
            # Calculate the dead zone width
            x_dead_zone_width = int(radius * self._dead_zone_x)
            
            # Create a semi-transparent yellow for the X dead zone
            x_dead_zone_color = QColor(255, 255, 0, 30)  # Yellow with 30/255 alpha
            painter.setPen(QPen(QColor(255, 255, 0, 80), 1))  # More opaque yellow for border
            painter.setBrush(QBrush(x_dead_zone_color))
            
            # Draw the X-axis dead zone rectangle
            x_dead_zone_rect = QRect(
                center_x - x_dead_zone_width,
                center_y - radius + 5,
                x_dead_zone_width * 2,
                2 * radius - 10
            )
            painter.drawRect(x_dead_zone_rect)
            
        # Draw Y-axis dead zone if set
        if self._dead_zone_y > 0.0:
            # Calculate the dead zone height
            y_dead_zone_height = int(radius * self._dead_zone_y)
            
            # Create a semi-transparent green for the Y dead zone
            y_dead_zone_color = QColor(0, 255, 0, 30)  # Green with 30/255 alpha
            painter.setPen(QPen(QColor(0, 255, 0, 80), 1))  # More opaque green for border
            painter.setBrush(QBrush(y_dead_zone_color))
            
            # Draw the Y-axis dead zone rectangle
            y_dead_zone_rect = QRect(
                center_x - radius + 5,
                center_y - y_dead_zone_height,
                2 * radius - 10,
                y_dead_zone_height * 2
            )
            painter.drawRect(y_dead_zone_rect)

        # Draw X and Y axes
        painter.setPen(QPen(QColor(180, 180, 180), 1))
        # X-axis (horizontal line)
        painter.drawLine(center_x - radius + 5, center_y, center_x + radius - 5, center_y)
        # Y-axis (vertical line)
        painter.drawLine(center_x, center_y - radius + 5, center_x, center_y + radius - 5)
        
        # Draw the center position marker
        painter.setPen(QPen(QColor(150, 150, 150), 1))
        
        # Draw crosshair at center
        painter.drawLine(center_x - 5, center_y, center_x + 5, center_y)
        painter.drawLine(center_x, center_y - 5, center_x, center_y + 5)
        
        # Calculate the handle position
        x, y = self._position
        handle_x = center_x + int(x * (size // 2 - self._handle_radius))
        handle_y = center_y - int(y * (size // 2 - self._handle_radius))  # Invert Y for screen coords
        
        # Set handle color based on whether it's in a dead zone
        if self._is_in_dead_zone:
            handle_color = QColor(200, 100, 100)  # Reddish when in dead zone
        elif self._is_in_x_dead_zone:
            handle_color = QColor(200, 200, 100)  # Yellowish when in X dead zone
        elif self._is_in_y_dead_zone:
            handle_color = QColor(100, 200, 100)  # Greenish when in Y dead zone
        else:
            handle_color = QColor(100, 150, 255)  # Bluish when outside all dead zones
        
        # Draw the handle
        painter.setPen(QPen(QColor(200, 200, 200), 2))
        painter.setBrush(QBrush(handle_color))
        painter.drawEllipse(QPoint(handle_x, handle_y), self._handle_radius, self._handle_radius)
        
        # Draw connection line from center to handle
        painter.setPen(QPen(QColor(150, 150, 150), 1, Qt.DashLine))
        painter.drawLine(center_x, center_y, handle_x, handle_y)
        
        # Display current coordinates near the handle
        painter.setPen(QColor(255, 255, 255))
        coord_text = f"({x:.2f}, {y:.2f})"
        
        # Add indicator for current state
        if self._is_in_dead_zone:
            coord_text += " [DEAD ZONE]"
        elif self._is_in_x_dead_zone:
            coord_text += " [X DEAD]"
        elif self._is_in_y_dead_zone:
            coord_text += " [Y DEAD]"
        elif self._exponential_x > 1.0 or self._exponential_y > 1.0:
            # Show percentage values instead of raw factors
            x_percent = self._exponential_x_percent
            y_percent = self._exponential_y_percent
            coord_text += f" [EXP {x_percent:.0f}%,{y_percent:.0f}%]"
            
        painter.drawText(handle_x + 15, handle_y, coord_text)
    
    def _draw_exponential_visualization(self, painter, center_x, center_y, radius):
        """Draw visualization of exponential response curve.
        
        Args:
            painter: QPainter instance
            center_x: X center of the joystick
            center_y: Y center of the joystick
            radius: Radius of the joystick area
        """
        # Save current painter state
        painter.save()
        
        # Use smaller radius for curves to ensure they stay within the circle
        curve_radius = int(radius * 0.85)
        
        # Use semi-transparent colors for better visibility
        x_curve_color = QColor(255, 80, 80, 180)  # Red with some transparency
        y_curve_color = QColor(80, 80, 255, 180)  # Blue with some transparency
        
        # Create a clipping path to limit drawing to inside the circle
        clip_path = QPainterPath()
        clip_path.addEllipse(center_x - radius, center_y - radius, radius * 2, radius * 2)
        painter.setClipPath(clip_path)
        
        # Draw X-axis exponential grid if enabled
        if self._exponential_x_percent > 0.0:
            # Set pen to a solid red line for the curve
            painter.setPen(QPen(x_curve_color, 2, Qt.SolidLine))
            
            # Create a path for the exponential curve using the standard expo formula
            path = QPainterPath()
            
            # Draw X-axis curve
            points = []
            expo_factor = self._exponential_x_percent / 100.0  # Convert to 0-1 range
            
            # Add many points to make the curve smooth
            for i in range(101):
                # Input from -1.0 to 1.0
                input_x = -1.0 + (i * 0.02)
                
                # Calculate output using the standard expo formula
                sign_x = 1.0 if input_x > 0.0 else -1.0
                abs_x = abs(input_x)
                # Standard expo formula: linear blend with cubic
                output_x = sign_x * (abs_x * (1.0 - expo_factor) + (abs_x ** 3) * expo_factor)
                
                # Calculate pixel positions (using smaller curve_radius to avoid edge overlap)
                px = center_x + int(input_x * curve_radius)  # X position based on input
                py = center_y - int(output_x * curve_radius)  # Y position based on output (inverted)
                
                points.append((px, py))
            
            # Create the path
            if points:
                path.moveTo(points[0][0], points[0][1])
                for px, py in points[1:]:
                    path.lineTo(px, py)
                    
            painter.drawPath(path)
            
            # Draw small label to indicate X-axis expo (moved inside for better positioning)
            painter.setPen(QPen(x_curve_color, 1))
            # Position label closer to the center to ensure it stays inside the circle
            label_x = center_x + int(curve_radius * 0.5)
            label_y = center_y - int(curve_radius * 0.5)
            painter.drawText(label_x, label_y, f"X:{self._exponential_x_percent:.0f}%")
            
        # Draw Y-axis exponential grid if enabled
        if self._exponential_y_percent > 0.0:
            # Set pen to a solid blue line for the curve (to distinguish from X)
            painter.setPen(QPen(y_curve_color, 2, Qt.SolidLine))
            
            # Create a path for the exponential curve using the standard expo formula
            path = QPainterPath()
            
            # Draw Y-axis curve
            points = []
            expo_factor = self._exponential_y_percent / 100.0  # Convert to 0-1 range
            
            # Add many points to make the curve smooth
            for i in range(101):
                # Input from -1.0 to 1.0
                input_y = -1.0 + (i * 0.02)
                
                # Calculate output using the standard expo formula
                sign_y = 1.0 if input_y > 0.0 else -1.0
                abs_y = abs(input_y)
                # Standard expo formula: linear blend with cubic
                output_y = sign_y * (abs_y * (1.0 - expo_factor) + (abs_y ** 3) * expo_factor)
                
                # Calculate pixel positions (using smaller curve_radius to avoid edge overlap)
                px = center_x + int(output_y * curve_radius)  # X position based on output
                py = center_y - int(input_y * curve_radius)  # Y position based on input (inverted)
                
                points.append((px, py))
            
            # Create the path
            if points:
                path.moveTo(points[0][0], points[0][1])
                for px, py in points[1:]:
                    path.lineTo(px, py)
                    
            painter.drawPath(path)
            
            # Draw small label to indicate Y-axis expo (moved inside for better positioning)
            painter.setPen(QPen(y_curve_color, 1))
            # Position label closer to the center to ensure it stays inside the circle
            label_x = center_x - int(curve_radius * 0.3)
            label_y = center_y - int(curve_radius * 0.5)
            painter.drawText(label_x, label_y, f"Y:{self._exponential_y_percent:.0f}%")
            
        # Draw 1:1 reference line (diagonal) with a dotted light gray line
        if self._exponential_x_percent > 0.0 or self._exponential_y_percent > 0.0:
            painter.setPen(QPen(QColor(150, 150, 150, 80), 1, Qt.DotLine))
            painter.drawLine(center_x - curve_radius, center_y + curve_radius, 
                            center_x + curve_radius, center_y - curve_radius)
        
        # Restore painter state (which also removes the clipping path)
        painter.restore()
    
    def __del__(self):
        """Destructor to clean up resources."""
        # Stop the update timer if running
        if self._update_timer.isActive():
            self._update_timer.stop()


class JoystickParameter(Parameter):
    """2D Joystick parameter for controlling x,y coordinate values.
    
    A parameter widget providing a 2D joystick control that reports
    normalized x,y coordinates in the range -1.0 to 1.0.
    
    Attributes:
        name (str): Display name of the parameter
        value (tuple): Current parameter value as (x, y) tuple
        joystick (JoystickWidget): The joystick control widget
        config (dict): Configuration dictionary with all settings
    """
    
    def __init__(self, name: str = "Unnamed", config: Optional[Dict] = None) -> None:
        """Initialize the joystick parameter widget.
        
        Args:
            name: Display name of the parameter
            config: Configuration dictionary with optional keys:
                - x_min: Minimum value for X axis (default: -1.0)
                - x_max: Maximum value for X axis (default: 1.0)
                - y_min: Minimum value for Y axis (default: -1.0)
                - y_max: Maximum value for Y axis (default: 1.0)
                - x_initial: Initial X position (default: 0.0)
                - y_initial: Initial Y position (default: 0.0)
                - size: Widget size in pixels (default: uses sizeHint)
                - return_to_center: Whether to return to center when released (default: True)
                - return_mode: Return-to-center mode - one of "none", "horizontal", "vertical", "both"
                - dead_zone: Circular dead zone value from 0.0 to 0.9 (default: 0.0)
                - dead_zone_x: X-axis specific dead zone from 0.0 to 0.9 (default: 0.0)
                - dead_zone_y: Y-axis specific dead zone from 0.0 to 0.9 (default: 0.0)
                - exponential_x: X-axis exponential percentage (0% = linear, 100% = max exponential)
                - exponential_y: Y-axis exponential percentage (0% = linear, 100% = max exponential)
                - update_frequency: Updates per second when pressed (default: 10 Hz)
        """
        super().__init__(name, config)
        config = config or {}
        self.config = config.copy()  # Store the config for serialization
        
        # Create layout for joystick (center aligned)
        joystick_layout = QVBoxLayout()
        joystick_layout.setContentsMargins(5, 5, 5, 5)
        
        # Create the joystick widget
        self.joystick = JoystickWidget()
        
        # Set custom size if provided
        if 'size' in config:
            size = config['size']
            self.joystick.setFixedSize(size, size)
            
        # Set initial position
        x_initial = config.get('x_initial', 0.0)
        y_initial = config.get('y_initial', 0.0)
        initial_pos = (float(x_initial), float(y_initial))
        
        self.value = initial_pos
        self.joystick.set_position(*initial_pos)
        
        # Configure return-to-center behavior
        return_mode = RETURN_MODE_BOTH  # Default behavior

        # Check for legacy return_to_center parameter
        if 'return_to_center' in config:
            if config['return_to_center']:
                return_mode = RETURN_MODE_BOTH
            else:
                return_mode = RETURN_MODE_NONE

        # Check for the newer return_mode parameter (overrides return_to_center)
        if 'return_mode' in config:
            mode = config['return_mode']
            if mode in (RETURN_MODE_NONE, RETURN_MODE_HORIZONTAL, RETURN_MODE_VERTICAL, RETURN_MODE_BOTH):
                return_mode = mode
                
        self.joystick.set_return_mode(return_mode)
        
        # Configure circular dead zone if provided
        if 'dead_zone' in config:
            dead_zone = float(config['dead_zone'])
            self.joystick.set_dead_zone(dead_zone)
            
        # Configure axis-specific dead zones if provided
        dead_zone_x = config.get('dead_zone_x', 0.0)
        dead_zone_y = config.get('dead_zone_y', 0.0)
        if dead_zone_x > 0.0 or dead_zone_y > 0.0:
            self.joystick.set_axis_dead_zones(float(dead_zone_x), float(dead_zone_y))
            
        # Configure exponential response if provided
        # Use percentage-based expo values (0-100%)
        expo_x_percent = config.get('exponential_x', 0.0)
        expo_y_percent = config.get('exponential_y', 0.0)
            
        if expo_x_percent > 0.0 or expo_y_percent > 0.0:
            self.joystick.set_exponential(float(expo_x_percent), float(expo_y_percent))
            
        # Configure update frequency if provided (new approach using Hz)
        if 'update_frequency' in config:
            frequency = float(config['update_frequency'])
            self.joystick.set_update_frequency(frequency)
        # For backward compatibility with update_interval
        elif 'update_interval' in config:
            interval_ms = int(config['update_interval'])
            # Convert from interval in ms to frequency in Hz
            if interval_ms > 0:
                frequency = 1000 / interval_ms
                self.joystick.set_update_frequency(frequency)
        
        # Connect signals
        self.joystick.positionChanged.connect(self._on_position_changed)
        
        # Add joystick to layout
        joystick_layout.addWidget(self.joystick)
        
        # Add to main layout (after the label from parent class)
        self.layout.addLayout(joystick_layout)
    
    def _on_position_changed(self, x: float, y: float) -> None:
        """Handle position changes from the joystick.
        
        Args:
            x: X position (-1.0 to 1.0)
            y: Y position (-1.0 to 1.0)
        """
        self.value = (x, y)
        self.valueChanged.emit(self.name, self.value)
    
    def set_value(self, value: Tuple[float, float]):
        """Set the joystick parameter value.
        
        Args:
            value: New value as (x, y) tuple
        """
        if isinstance(value, tuple) and len(value) == 2:
            x, y = value
            self.joystick.set_position(x, y)
        else:
            raise ValueError("Value must be a tuple of (x, y)")
    
    def get_value(self) -> Tuple[float, float]:
        """Get the current joystick parameter value.
        
        Returns:
            The current value as (x, y) tuple
        """
        return self.value
    
    def set_config(self, config: Dict):
        """Set the configuration for the joystick parameter.
        
        Args:
            config: Configuration dictionary with keys as described in __init__
        """
        super().set_config(config)
        
        # Update the joystick widget configuration
        self.joystick.set_return_mode(config.get('return_mode', RETURN_MODE_BOTH))
        self.joystick.set_dead_zone(config.get('dead_zone', 0.0))
        self.joystick.set_axis_dead_zones(config.get('dead_zone_x', 0.0), config.get('dead_zone_y', 0.0))
        self.joystick.set_exponential(config.get('exponential_x', 1.0), config.get('exponential_y', 1.0))
        self.joystick.set_update_frequency(config.get('update_frequency', 10.0))
        
        # Update size if specified
        if 'size' in config:
            size = config['size']
            self.joystick.setFixedSize(size, size)
        
        # Update initial position
        x_initial = config.get('x_initial', 0.0)
        y_initial = config.get('y_initial', 0.0)
        self.joystick.set_position(float(x_initial), float(y_initial))
    
    def get_config(self) -> Dict:
        """Get the current configuration of the joystick parameter.
        
        Returns:
            Configuration dictionary with current settings
        """
        config = super().get_config()
        config.update({
            'return_mode': self.joystick.get_return_mode(),
            'dead_zone': self.joystick.get_dead_zone(),
            'dead_zone_x': self.joystick._dead_zone_x,
            'dead_zone_y': self.joystick._dead_zone_y,
            'exponential_x': self.joystick._exponential_x,
            'exponential_y': self.joystick._exponential_y,
            'update_frequency': self.joystick.get_update_frequency(),
            'x_initial': self.value[0],
            'y_initial': self.value[1],
            # 'size' is not included here as it may be fixed size
        })
        return config
    
    def sizeHint(self) -> QSize:
        """Suggest a default size for the parameter widget.
        
        Returns:
            The suggested size
        """
        return QSize(150, 150)
    
    def paint(self, painter, option, index):
        """Paint the parameter widget.
        
        Args:
            painter: QPainter instance
            option: Style option
            index: Model index
        """
        # Call base class implementation
        super().paint(painter, option, index)
        
        # Draw the joystick widget manually
        self.joystick.paint(painter, option.rect)