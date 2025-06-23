import os
# Fix OpenCV Qt conflicts by setting environment variable before importing cv2
# os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = ""

from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtSignal
import numpy as np

# Import cv2 after setting environment variable
try:
    import cv2
    HAS_CV2 = True
except ImportError:
    cv2 = None
    HAS_CV2 = False
    print("Warning: OpenCV not available. Some image conversion features will be limited.")

from .base_display import BaseDisplay


class ImageDisplay(BaseDisplay):
    """
    A widget for displaying images within the PyQt Live Tuner.
    
    This widget can display images from various sources:
    - NumPy arrays (from OpenCV or other libraries)
    - File paths (common image formats)
    - QImage objects
    
    Features:
    - Resizable display
    - Signal when image is clicked
    
    Config options:
    - title (str): Title for the display widget
    - size (tuple): Default size as (width, height)
    - show_title (bool): Whether to show the title
    - maintain_aspect_ratio (bool): Whether to maintain image aspect ratio when resizing
    """
    
    image_clicked = pyqtSignal(int, int)  # Emits x, y coordinates when image is clicked
    
    def __init__(self, parent=None, config=None):
        """
        Initialize the image display widget.
        
        Args:
            parent: Parent widget (default: None)
            config: Configuration dictionary with options (default: None)
                   See class docstring for available options
        """
        # Default configuration specific to ImageDisplay
        self.image_config = {
            "title": "Image Display",
            "maintain_aspect_ratio": True,
        }
        
        # Create full config
        full_config = self.image_config.copy()
        if config is not None:
            full_config.update(config)
        
        # Initialize base display with config values
        super().__init__(parent=parent, config=full_config)
        
        # Set additional properties
        self.maintain_aspect_ratio = full_config.get("maintain_aspect_ratio", True)
        self.image = None
        self.pixmap = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components specific to ImageDisplay"""
        # Image display label
        self.image_label = QLabel()
        self.image_label.setMinimumSize(self.default_size[0], self.default_size[1])
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.mousePressEvent = self._on_image_click
        
        # Add image label to content layout (provided by BaseDisplay)
        self.content_layout.addWidget(self.image_label)
    
    def display_image(self, image_data):
        """
        Display an image from various possible sources
        
        Args:
            image_data: Can be a numpy array (BGR or RGB), file path, or QImage
        """
        if image_data is None:
            self.clear()
            return
            
        self.image = image_data
        
        # Convert various image types to QPixmap
        if isinstance(image_data, np.ndarray):
            self.pixmap = self._numpy_to_pixmap(image_data)
        elif isinstance(image_data, str):
            # Assume it's a file path
            self.pixmap = QPixmap(image_data)
        elif isinstance(image_data, QImage):
            self.pixmap = QPixmap.fromImage(image_data)
        elif isinstance(image_data, QPixmap):
            self.pixmap = image_data
        else:
            raise TypeError(f"Unsupported image type: {type(image_data)}")
        
        # Show the image with appropriate sizing
        self._update_display()
    
    def _numpy_to_pixmap(self, np_img):
        """Convert a numpy array to QPixmap"""
        # Check if grayscale (2D array)
        if len(np_img.shape) == 2:
            # Grayscale image
            height, width = np_img.shape
            bytes_per_line = width
            img = QImage(np_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
        else:
            # Color image
            # Check if the image dimensions need to be inferred from total size
            if len(np_img.shape) == 1:
                # One-dimensional array - need to infer dimensions
                total_size = np_img.size
                
                # Try to calculate dimensions based on common aspect ratios
                # Assume 3 channels (RGB) or 4 channels (RGBA)
                channels = 3  # Default to RGB
                
                # Check if size is divisible by 4 (RGBA)
                if total_size % 4 == 0:
                    channels = 4
                    pixels = total_size // 4
                # Check if size is divisible by 3 (RGB)
                elif total_size % 3 == 0:
                    channels = 3
                    pixels = total_size // 3
                else:
                    # If not divisible by 3 or 4, assume single channel grayscale
                    channels = 1
                    pixels = total_size
                
                # Try common resolutions to find a match
                common_widths = [640, 960, 1280, 1920, 3840]
                
                for width in common_widths:
                    if pixels % width == 0:
                        height = pixels // width
                        # Reshape the array to inferred dimensions
                        if channels > 1:
                            np_img = np_img.reshape(height, width, channels)
                        else:
                            np_img = np_img.reshape(height, width)
                        break
                else:
                    # If no common width works, try square root for an approximate match
                    width = int(np.sqrt(pixels))
                    height = pixels // width
                    # Ensure the reshaping would work
                    if width * height == pixels:
                        if channels > 1:
                            np_img = np_img.reshape(height, width, channels)
                        else:
                            np_img = np_img.reshape(height, width)
                    else:
                        # Last resort: just use the raw data without reshaping
                        raise ValueError(f"Cannot determine image dimensions from array size {total_size}")
            
            # Now process the correctly shaped image
            height, width = np_img.shape[:2]
            
            if len(np_img.shape) == 2:
                # Grayscale
                bytes_per_line = width
                img = QImage(np_img.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            elif np_img.shape[2] == 1:
                # Single channel but in 3D array
                bytes_per_line = width
                np_img_2d = np_img.reshape(height, width)
                img = QImage(np_img_2d.data, width, height, bytes_per_line, QImage.Format_Grayscale8)
            elif np_img.shape[2] == 3:  # Color image (BGR)
                if HAS_CV2:
                    # Convert BGR to RGB
                    rgb_img = cv2.cvtColor(np_img, cv2.COLOR_BGR2RGB)
                    bytes_per_line = width * 3
                    img = QImage(rgb_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
                else:
                    # Assume it's already RGB if OpenCV is not available
                    bytes_per_line = width * 3
                    img = QImage(np_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
            elif np_img.shape[2] == 4:  # RGBA image
                bytes_per_line = width * 4
                img = QImage(np_img.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
            else:
                raise ValueError(f"Unsupported image format with {np_img.shape[2]} channels")
        
        return QPixmap.fromImage(img)
    
    def _update_display(self):
        """Update the image display with current pixmap"""
        if self.pixmap and not self.pixmap.isNull():
            if self.maintain_aspect_ratio:
                self.image_label.setPixmap(
                    self.pixmap.scaled(
                        self.image_label.width(),
                        self.image_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
            else:
                self.image_label.setPixmap(
                    self.pixmap.scaled(
                        self.image_label.width(),
                        self.image_label.height(),
                        Qt.IgnoreAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
    
    def clear(self):
        """Clear the displayed image"""
        self.image = None
        self.pixmap = None
        self.image_label.clear()
    
    def _on_image_click(self, event):
        """Handle mouse clicks on the image"""
        if self.pixmap and not self.pixmap.isNull():
            # Get position relative to the actual image
            label_width = self.image_label.width()
            label_height = self.image_label.height()
            
            pixmap_displayed = self.image_label.pixmap()
            img_width = pixmap_displayed.width()
            img_height = pixmap_displayed.height()
            
            # Calculate the offset if the image is centered
            x_offset = (label_width - img_width) // 2
            y_offset = (label_height - img_height) // 2
            
            # Calculate click position on the image
            x = event.x() - x_offset
            y = event.y() - y_offset
            
            # Only emit if click is inside the image
            if 0 <= x < img_width and 0 <= y < img_height:
                # Scale coordinates to original image size if needed
                orig_width = self.pixmap.width()
                orig_height = self.pixmap.height()
                
                if img_width != orig_width or img_height != orig_height:
                    x = int(x * orig_width / img_width)
                    y = int(y * orig_height / img_height)
                
                self.image_clicked.emit(x, y)
    
    def resizeEvent(self, event):
        """Handle resize events to maintain proper image display"""
        super().resizeEvent(event)
        if self.pixmap and not self.pixmap.isNull():
            self._update_display()
    
    def save_state(self):
        """Save the current state of the display"""
        state = super().save_state()
        state.update({
            "maintain_aspect_ratio": self.maintain_aspect_ratio,
        })
        return state
    
    def load_state(self, state):
        """Load a previously saved state"""
        super().load_state(state)
        
        if "maintain_aspect_ratio" in state:
            self.maintain_aspect_ratio = state["maintain_aspect_ratio"]
            if self.pixmap and not self.pixmap.isNull():
                self._update_display()


# Example usage
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    # Create an image display widget with custom config
    config = {
        "title": "Custom Image Viewer",
        "size": (800, 600),
        "maintain_aspect_ratio": True,
        "show_title": True
    }
    image_display = ImageDisplay(config=config)
    
    # Create a sample numpy array (a gradient image)
    width, height = 640, 480
    image = np.zeros((height, width, 3), dtype=np.uint8)
    for i in range(height):
        for j in range(width):
            image[i, j] = [i % 256, j % 256, (i + j) % 256]
    
    # Display the image
    image_display.display_image(image)
    
    # Show the widget
    image_display.show()
    
    sys.exit(app.exec_())