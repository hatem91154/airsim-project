import sys
import os
import numpy as np

# Add parent directory to path to ensure we can import from pyqt_live_tuner
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

from pyqt_live_tuner.displays.image import ImageDisplay

class SimpleImageExample(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Simple Image Display Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Create central widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Create image displays with different configurations
        image_layout = QHBoxLayout()
        
        # Image display 1: Default configuration
        self.image_display1 = ImageDisplay(config={
            "title": "Default Configuration",
            "size": (300, 300),
            "show_title": True
        })
        
        # Image display 2: Custom configuration
        self.image_display2 = ImageDisplay(config={
            "title": "Custom Configuration",
            "size": (300, 300),
            "show_title": True,
            "maintain_aspect_ratio": False
        })
        
        image_layout.addWidget(self.image_display1)
        image_layout.addWidget(self.image_display2)
        main_layout.addLayout(image_layout)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Create sample images button
        create_image_btn = QPushButton("Create Sample Images")
        create_image_btn.clicked.connect(self.create_sample_images)
        button_layout.addWidget(create_image_btn)
        
        # Create gradient image button
        gradient_btn = QPushButton("Create Gradient")
        gradient_btn.clicked.connect(self.create_gradient)
        button_layout.addWidget(gradient_btn)
        
        # Create checkerboard image button
        checker_btn = QPushButton("Create Checkerboard")
        checker_btn.clicked.connect(self.create_checkerboard)
        button_layout.addWidget(checker_btn)
        
        # Clear images button
        clear_btn = QPushButton("Clear Images")
        clear_btn.clicked.connect(self.clear_images)
        button_layout.addWidget(clear_btn)
        
        main_layout.addLayout(button_layout)
        
        # Set central widget
        self.setCentralWidget(central_widget)
        
        # Create initial images
        self.create_sample_images()
    
    def create_sample_images(self):
        """Create and display sample images with shapes"""
        width, height = 640, 480
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        # Add some shapes and colors
        # Background gradient
        for i in range(height):
            for j in range(width):
                image[i, j] = [
                    int(i * 255 / height),
                    int(j * 255 / width),
                    int((i + j) * 255 / (height + width))
                ]
        
        # Add shapes if OpenCV is available
        try:
            import cv2
            # Circle
            cv2.circle(image, (width//4, height//4), 80, (0, 0, 255), -1)
            # Rectangle
            cv2.rectangle(image, (width//2, height//2), (width//2 + 150, height//2 + 100), (0, 255, 0), -1)
            # Line
            cv2.line(image, (50, height-50), (width-50, height-100), (255, 255, 255), 5)
            # Text
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(image, "ImageDisplay Test", (width//4, 50), font, 1, (255, 255, 255), 2)
        except ImportError:
            # If OpenCV is not available, just use the gradient
            pass
        
        # Display the image
        self.image_display1.display_image(image)
        self.image_display2.display_image(image)
    
    def create_gradient(self):
        """Create and display gradient images"""
        width, height = 640, 480
        
        # Create radial gradient
        image1 = np.zeros((height, width, 3), dtype=np.uint8)
        center_x, center_y = width // 2, height // 2
        max_dist = np.sqrt(center_x**2 + center_y**2)
        
        for i in range(height):
            for j in range(width):
                dist = np.sqrt((j - center_x)**2 + (i - center_y)**2)
                norm_dist = dist / max_dist
                image1[i, j] = [
                    int((1 - norm_dist) * 255),
                    int(norm_dist * 255),
                    int(abs(np.sin(norm_dist * np.pi)) * 255)
                ]
        
        # Create horizontal gradient
        image2 = np.zeros((height, width, 3), dtype=np.uint8)
        for i in range(height):
            for j in range(width):
                image2[i, j] = [
                    int(j * 255 / width),
                    int((height - i) * 255 / height),
                    int((i + j) * 255 / (height + width))
                ]
        
        # Display the images
        self.image_display1.display_image(image1)
        self.image_display2.display_image(image2)
    
    def create_checkerboard(self):
        """Create and display checkerboard pattern"""
        width, height = 640, 480
        cell_size = 40
        
        # Create checkerboard
        image = np.zeros((height, width, 3), dtype=np.uint8)
        
        for i in range(0, height, cell_size):
            for j in range(0, width, cell_size):
                color = 255 if ((i // cell_size) + (j // cell_size)) % 2 == 0 else 0
                image[i:i+cell_size, j:j+cell_size] = color
        
        # Display the same image in both displays
        self.image_display1.display_image(image)
        self.image_display2.display_image(image)
    
    def clear_images(self):
        """Clear both image displays"""
        self.image_display1.clear()
        self.image_display2.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SimpleImageExample()
    window.show()
    sys.exit(app.exec_())